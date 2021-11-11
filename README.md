# Rebind-KWin-Activities
A simple python + kwin script that puts windows back in their proper activities after kwin crashes/restarts

# Background
It is often annoying that after KWin crashes, all windows go to "all activities" despite the task manager having the proper settings, but kwin does not and looses these settings. Thus you gotta manually hit Alt+f3 on every window and put them in their proper activity.

This python script collects window and activity data from wmctrl + xprop and then uses a kwin script to assign the activities automatically. Then output a report of the results. Activitiy data is only assigned to windows where kwin is set to all activities, and only if the activity still exists.

# Usage

You can simply run the script with python3 as long as the js file is in same folder as the py file.

For convenience of launching from the start menu, a .desktop file is included. Place it in: 

```~/.local/share/applications/```

and the py and js file in:

```~/.local/share/rebind_kwin_activities/```

