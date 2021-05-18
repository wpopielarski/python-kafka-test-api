import logging
import py4j.java_gateway as JG


def ref_scala_object(jvm_handle: JG.JVMView, object_name: str) -> JG.JavaObject:
    clazz = jvm_handle.java.lang.Thread.currentThread().getContextClassLoader().loadClass(f"{object_name}$")
    ff = clazz.getDeclaredField("MODULE$")
    return ff.get(None)
