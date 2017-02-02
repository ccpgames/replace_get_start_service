# replace_get_start_service
Python script for replacing Get/Start Service calls.

Replaces sm.GetService("<service>") and sm.StartService("<service>") calls with Get<service>Service
and Start<service>Service calls, adding the necessary import at the top.

The script scans for all .py files in the current working directory and its subdirectories. If calls p4 edit
for any file it needs to change.

The script takes one argument - the name of the service to look for.