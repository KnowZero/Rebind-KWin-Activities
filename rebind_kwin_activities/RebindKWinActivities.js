let activity_dict = {};


workspace.activities.forEach(function (item) {
    activity_dict[item]=1;
});

const clients = workspace.clientList();



callDBus('org.kde.KWin.Script.RebindKWinActivities', '/callback', 'org.kde.kwin.Script', 'WindowList', function (wlist) {
    let window_dict = {};
    let wid_length = 0;
    
    wlist.forEach(function (item) {
        wid_length = item.wid.length-2;
        window_dict[item.wid]=item;
    });
    
    let return_results = [];
    
    for (var i = 0; i < clients.length; i++) {

        let wid = '0x'+clients[i].windowId.toString(16).padStart(wid_length,'0');
        let rec = { wid:wid, pid:clients[i].pid, title:clients[i].caption, result:'0' };

        if (clients[i].activities.length == 0) {

            if (window_dict[wid]) {
                rec.result='1';
                
                let add_activities = [];

                window_dict[wid].aid.forEach(function (act) {
                    if (activity_dict[act] === 1) {
                        add_activities.push(act);
                    } else {
                        return '3';
                    }
                });

                //console.log("ITEM", wid, clients[i].caption )
                //console.log("ITEM", clients[i].activities, wid, window_dict[wid].pid, clients[i].caption )
                //print(clients[i].caption, clients[i].activities, window_list[clients[i].windowId]['wid'], clients[i].pid, clients[i].internalId, clients[i].windowId );
                
                clients[i].activities = add_activities;
                
            } else {
                if (clients[i].normalWindow) {
                    rec.result='9';
                } else {
                    rec.result='8';
                }
                //console.log("FAIL", clients[i].normalWindow, clients[i].caption, clients[i].activities );
            }

        } else {
            rec.result='2';
        }

        return_results.push(rec);
    }

    
    callDBus('org.kde.KWin.Script.RebindKWinActivities', '/callback', 'org.kde.kwin.Script', 'Finish', return_results, function () {
        print("RebindKWinActivitie has finished!")

    } )
} )


