# For Macs: Change LD_LIBRARY_PATH -> DYLD_LIBRARY_PATH
echo export LD_LIBRARY_PATH=\$VIRTUAL_ENV/lib:\$LD_LIBRARY_PATH > $HOME/env/gnomon/bin/activate
echo export PYTHONPATH=\$VIRTUAL_ENV/lib:\$PYTHONPATH > $HOME/env/gnomon/bin/activate

