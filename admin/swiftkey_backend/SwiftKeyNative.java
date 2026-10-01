import com.alibaba.fastjson.JSON;
import com.github.unidbg.AndroidEmulator;
import com.github.unidbg.Emulator;
import com.github.unidbg.Module;
import com.github.unidbg.arm.Arm64Svc;
import com.github.unidbg.arm.backend.Unicorn2Factory;
import com.github.unidbg.arm.context.RegisterContext;
import com.github.unidbg.linux.android.AndroidARM64Emulator;
import com.github.unidbg.linux.android.AndroidResolver;
import com.github.unidbg.linux.android.dvm.AbstractJni;
import com.github.unidbg.linux.android.dvm.BaseVM;
import com.github.unidbg.linux.android.dvm.DvmClass;
import com.github.unidbg.linux.android.dvm.DvmObject;
import com.github.unidbg.linux.android.dvm.StringObject;
import com.github.unidbg.linux.android.dvm.VM;
import com.github.unidbg.linux.android.dvm.VaList;
import com.github.unidbg.linux.android.dvm.array.ArrayObject;
import com.github.unidbg.linux.android.dvm.array.ByteArray;
import com.sun.jna.Pointer;

import java.io.File;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashSet;
import java.util.IdentityHashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Native adapter for the original Fluency engine shipped in SwiftKey 9.10.49.20. */
@SuppressWarnings("unchecked")
public final class SwiftKeyNative extends AbstractJni implements AutoCloseable {
    private static final String PREFIX = "com/microsoft/fluency/";
    private static final int JNI_SET_BYTE_ARRAY_REGION_OFFSET = 0x680;
    private final AndroidEmulator emulator;
    private final VM vm;
    private final Field pendingException;
    private final Method deleteLocalRefs;
    private final Map<DvmObject<?>, Long> peers = new IdentityHashMap<>();
    private RuntimeException callbackFailure;

    private static final class SwiftKeyEmulator extends AndroidARM64Emulator {
        SwiftKeyEmulator(File root) {
            super("local.swiftkey.lm", root, Arrays.asList(new Unicorn2Factory(true)));
        }
    }

    SwiftKeyNative(File library, File root) throws Exception {
        emulator = new SwiftKeyEmulator(root);
        emulator.setTimeout(60_000_000L);
        emulator.getMemory().setLibraryResolver(new AndroidResolver(23));
        vm = emulator.createDalvikVM();
        vm.setJni(this);
        installByteArrayRegionHandler();
        pendingException = BaseVM.class.getDeclaredField("throwable");
        pendingException.setAccessible(true);
        deleteLocalRefs = BaseVM.class.getDeclaredMethod("deleteLocalRefs");
        deleteLocalRefs.setAccessible(true);
        DvmClass collection =
                vm.resolveClass("java/util/Collection", vm.resolveClass("java/lang/Iterable"));
        vm.resolveClass("java/util/HashSet", vm.resolveClass("java/util/Set", collection));
        vm.resolveClass("java/util/HashMap", vm.resolveClass("java/util/Map"));
        vm.resolveClass("java/util/ArrayList", vm.resolveClass("java/util/List", collection));
        vm.loadLibrary(library, true).callJNI_OnLoad(emulator);
        invoke(vm.resolveClass(PREFIX + "Fluency"), "initIDs()V");
        invoke(vm.resolveClass(PREFIX + "internal/InternalFluency"), "initIDs()V");
    }

    /** Handle empty JNI byte-array regions without dereferencing a null buffer. */
    private void installByteArrayRegionHandler() {
        Pointer handler =
                emulator.getSvcMemory()
                        .registerSvc(
                                new Arm64Svc() {
                                    @Override
                                    public long handle(Emulator<?> emu) {
                                        RegisterContext context = emu.getContext();
                                        ByteArray array = vm.getObject(context.getIntArg(1));
                                        int start = context.getIntArg(2);
                                        int length = context.getIntArg(3);
                                        if (array == null
                                                || start < 0
                                                || length < 0
                                                || (long) start + length > array.length()) {
                                            throw remember(
                                                    new IllegalArgumentException(
                                                            "Invalid JNI byte array region"));
                                        }
                                        if (length != 0) {
                                            Pointer buffer = context.getPointerArg(4);
                                            if (buffer == null) {
                                                throw remember(
                                                        new IllegalArgumentException(
                                                                "Missing JNI byte array buffer"));
                                            }
                                            array.setData(start, buffer.getByteArray(0, length));
                                        }
                                        return 0;
                                    }
                                });
        vm.getJNIEnv().getPointer(0).setPointer(JNI_SET_BYTE_ARRAY_REGION_OFFSET, handler);
    }

    /** Check exceptions before unidbg discards local references. */
    private DvmObject<?> invoke(DvmObject<?> receiver, String method, Object... arguments)
            throws Exception {
        callbackFailure = null;
        DvmClass type =
                receiver instanceof DvmClass ? (DvmClass) receiver : receiver.getObjectType();
        List<Object> args = new ArrayList<>();
        args.add(vm.getJNIEnv());
        args.add(vm.addLocalObject(receiver));
        for (Object arg : arguments)
            args.add(arg instanceof DvmObject<?> ? vm.addLocalObject((DvmObject<?>) arg) : arg);
        try {
            Number result =
                    Module.emulateFunction(
                            emulator,
                            type.findNativeFunction(emulator, method).peer,
                            args.toArray());
            if (callbackFailure != null) throw callbackFailure;
            DvmObject<?> error = (DvmObject<?>) pendingException.get(vm);
            if (error != null)
                throw new IllegalStateException(
                        error.getObjectType().getClassName() + ": " + error.getValue());
            return vm.getObject(result.intValue());
        } finally {
            deleteLocalRefs.invoke(vm);
        }
    }

    private RuntimeException remember(RuntimeException error) {
        callbackFailure = error;
        return error;
    }

    private static Object plain(Object value) {
        if (value instanceof DvmObject<?>) return plain(((DvmObject<?>) value).getValue());
        if (value instanceof DvmObject<?>[]) {
            List<Object> result = new ArrayList<>();
            for (Object item : (DvmObject<?>[]) value) result.add(plain(item));
            return result;
        }
        if (value instanceof Iterable<?>) {
            List<Object> result = new ArrayList<>();
            for (Object item : (Iterable<?>) value) result.add(plain(item));
            return result;
        }
        return value;
    }

    @Override
    public DvmObject<?> callStaticObjectMethodV(
            BaseVM vm, DvmClass type, String signature, VaList arguments) {
        if (signature.equals(
                PREFIX
                        + "LoggingListener$Level->values()[Lcom/microsoft/fluency/LoggingListener$Level;"))
            return new ArrayObject(type.newObject(0), type.newObject(1), type.newObject(2));
        if (signature.equals("java/lang/Long->valueOf(J)Ljava/lang/Long;"))
            return type.newObject(arguments.getLongArg(0));
        try {
            return super.callStaticObjectMethodV(vm, type, signature, arguments);
        } catch (RuntimeException error) {
            throw remember(error);
        }
    }

    @Override
    public int callIntMethodV(BaseVM vm, DvmObject<?> object, String signature, VaList arguments) {
        if (signature.endsWith("->ordinal()I") || signature.endsWith("->version()I"))
            return ((Number) object.getValue()).intValue();
        try {
            return super.callIntMethodV(vm, object, signature, arguments);
        } catch (RuntimeException error) {
            throw remember(error);
        }
    }

    @Override
    public long getLongField(BaseVM vm, DvmObject<?> object, String signature) {
        if (signature.endsWith("->peer:J")) return peers.getOrDefault(object, 0L);
        try {
            return super.getLongField(vm, object, signature);
        } catch (RuntimeException error) {
            throw remember(error);
        }
    }

    @Override
    public void setLongField(BaseVM vm, DvmObject<?> object, String signature, long value) {
        if (signature.endsWith("->peer:J")) {
            peers.put(object, value);
            return;
        }
        try {
            super.setLongField(vm, object, signature, value);
        } catch (RuntimeException error) {
            throw remember(error);
        }
    }

    @Override
    public DvmObject<?> getObjectField(BaseVM vm, DvmObject<?> object, String signature) {
        if (signature.equals(PREFIX + "Term->term:Ljava/lang/String;"))
            return new StringObject(vm, (String) object.getValue());
        if (signature.equals(PREFIX + "Term->encodings:Ljava/util/HashSet;"))
            return vm.resolveClass("java/util/HashSet").newObject(new HashSet<DvmObject<?>>());
        try {
            return super.getObjectField(vm, object, signature);
        } catch (RuntimeException error) {
            throw remember(error);
        }
    }

    @Override
    public DvmObject<?> callObjectMethodV(
            BaseVM vm, DvmObject<?> object, String signature, VaList arguments) {
        if (signature.endsWith("->iterator()Ljava/util/Iterator;"))
            return vm.resolveClass("java/util/Iterator")
                    .newObject(((Iterable<?>) object.getValue()).iterator());
        if (signature.endsWith("->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;"))
            return ((Map<DvmObject<?>, DvmObject<?>>) object.getValue())
                    .put(arguments.getObjectArg(0), arguments.getObjectArg(1));
        try {
            return super.callObjectMethodV(vm, object, signature, arguments);
        } catch (RuntimeException error) {
            throw remember(error);
        }
    }

    @Override
    public boolean callBooleanMethodV(
            BaseVM vm, DvmObject<?> object, String signature, VaList arguments) {
        if (signature.endsWith("->add(Ljava/lang/Object;)Z"))
            return ((Collection<DvmObject<?>>) object.getValue()).add(arguments.getObjectArg(0));
        try {
            return super.callBooleanMethodV(vm, object, signature, arguments);
        } catch (RuntimeException error) {
            throw remember(error);
        }
    }

    @Override
    public DvmObject<?> newObjectV(BaseVM vm, DvmClass type, String signature, VaList arguments) {
        if (signature.equals(PREFIX + "internal/NgramExport$OffsetSize-><init>(II)V"))
            return type.newObject(new int[] {arguments.getIntArg(0), arguments.getIntArg(1)});
        if (signature.equals(PREFIX + "internal/NgramExport$NgramNode-><init>(III)V"))
            return type.newObject(
                    new int[] {
                        arguments.getIntArg(0), arguments.getIntArg(1), arguments.getIntArg(2)
                    });
        if (signature.startsWith(PREFIX + "internal/NgramExport-><init>")) {
            Map<String, Object> result = new LinkedHashMap<>();
            String[] keys = {"word_data", "words", "encoding_sets", "encodings", "ngram_nodes"};
            for (int i = 0; i < keys.length; i++)
                result.put(keys[i], plain(arguments.getObjectArg(i)));
            return type.newObject(result);
        }
        if (signature.equals(
                PREFIX
                        + "internal/ModelData-><init>(Lcom/microsoft/fluency/internal/NgramExport;JJ)V")) {
            Map<String, Object> result = new LinkedHashMap<>();
            DvmObject<?> ngrams = arguments.getObjectArg(0);
            result.put("native_ngram_export_present", ngrams != null);
            if (ngrams == null) {
                Map<String, Object> empty = new LinkedHashMap<>();
                empty.put("word_data", "");
                for (String key :
                        Arrays.asList("words", "encoding_sets", "encodings", "ngram_nodes"))
                    empty.put(key, new ArrayList<>());
                result.put("model", empty);
            } else result.put("model", ngrams.getValue());
            result.put("first_trained_unix_seconds", arguments.getLongArg(1));
            result.put("last_trained_unix_seconds", arguments.getLongArg(2));
            return type.newObject(result);
        }
        if (signature.startsWith(PREFIX) && signature.endsWith("<init>()V"))
            return type.newObject(null);
        if (signature.startsWith(PREFIX) && signature.endsWith("<init>(J)V")) {
            DvmObject<?> result = type.newObject(null);
            peers.put(result, arguments.getLongArg(0));
            return result;
        }
        if (signature.equals("java/util/HashMap-><init>()V"))
            return type.newObject(new LinkedHashMap<DvmObject<?>, DvmObject<?>>());
        if (signature.startsWith("java/util/HashSet-><init>"))
            return type.newObject(new HashSet<DvmObject<?>>());
        if (signature.equals(PREFIX + "Term-><init>(Ljava/util/Set;Ljava/lang/String;)V"))
            return type.newObject(arguments.getObjectArg(1).getValue());
        try {
            return super.newObjectV(vm, type, signature, arguments);
        } catch (RuntimeException error) {
            throw remember(error);
        }
    }

    private void extract(Path input, Path output) throws Exception {
        byte[] data = Files.readAllBytes(input);
        DvmObject<?> result =
                invoke(
                        vm.resolveClass(PREFIX + "internal/InternalFluency"),
                        "extractModelData([B)Lcom/microsoft/fluency/internal/ModelData;",
                        new ByteArray(vm, data));
        if (result == null) throw new IllegalStateException("Native export returned no model");
        Map<String, Object> out = (Map<String, Object>) result.getValue();
        out.put(
                "engine_version",
                invoke(vm.resolveClass(PREFIX + "Fluency"), "getVersion()Ljava/lang/String;")
                        .getValue());
        out.put(
                "engine_source_version",
                invoke(vm.resolveClass(PREFIX + "Fluency"), "getSourceVersion()Ljava/lang/String;")
                        .getValue());
        Files.writeString(
                output,
                JSON.toJSONString(out),
                StandardCharsets.UTF_8,
                StandardOpenOption.CREATE_NEW);
    }

    @Override
    public void close() throws Exception {
        emulator.close();
    }

    public static void main(String[] args) {
        try {
            if (args.length != 5 || !args[0].equals("extract")) {
                throw new IllegalArgumentException("extract library root input output");
            }
            try (SwiftKeyNative adapter =
                    new SwiftKeyNative(new File(args[1]), new File(args[2]))) {
                adapter.extract(Path.of(args[3]), Path.of(args[4]));
            }
        } catch (Exception error) {
            System.err.println(error.getClass().getSimpleName() + ": " + error.getMessage());
            System.exit(1);
        }
    }
}
