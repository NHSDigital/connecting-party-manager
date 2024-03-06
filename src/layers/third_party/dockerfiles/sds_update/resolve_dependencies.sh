LD_DEPENDENCY_TREE=$(LD_TRACE_LOADED_OBJECTS=1 /lib64/ld-linux-x86-64.so.2 /lib64/libldap-2.4.so.2)
LD_DEPENDENCIES=$(echo ${LD_DEPENDENCY_TREE} | xargs python resolve_dependencies.py)
for file in ${LD_DEPENDENCIES};
    do cp $file /usr/extras/;
done
cp /lib64/libldap* /usr/extras/
