//---------------------------------------------
// daeduck model scene id: 20170926103844839931304
//---------------------------------------------

//global init settings
var LISTENING = false;
var T_Live_Fire_Alarm = {};
var T_Live_Gas_Alarm = {};
var CURRENT_LEVEL = 'world';
var BASE_URL = "http://192.168.86.24:9006/";
//var BASE_URL = "http://192.168.236.1:9006/";
var T_Banner_List = {};
var T_Fly_List = {}

util.addEventListener("levelchange", function (event) {
	if (event.ClsID == ObjectFactory.CLSID_WORLD) {
		CURRENT_LEVEL = 'world';
	} else if (event.ClsID == ObjectFactory.CLSID_BUILDING) {
		CURRENT_LEVEL = 'building';
	} else if (event.ClsID == ObjectFactory.CLSID_FLOORPLAN) {
		CURRENT_LEVEL = 'floor';
	}
})

function get_building_index_by_name(building_name) {
	var building_index = -1
		if (building_name == 'P2B') {
			building_index = 8
		}
		if (building_name == 'P2A') {
			building_index = 7
		}
		if (building_name == 'Reception') {
			building_index = 11
		}
		return building_index
}

function get_floor_by_name(building_name, obj_name) {
	var floor_index = 0
		if (building_name == 'P2B') {
			if (string.contains(obj_name, '1F')) {
				floor_index = 0;
			}
			if (string.contains(obj_name, '2F')) {
				floor_index = 1;
			}
			if (string.contains(obj_name, '3F')) {
				floor_index = 2;
			}
		} else {
			if (string.contains(obj_name, '1F')) {
				floor_index = 1;
			}
			if (string.contains(obj_name, '2F')) {
				floor_index = 2;
			}
			if (string.contains(obj_name, '3F')) {
				floor_index = 3;
			}
		}
		return floor_index;
}

//show banner on top of object
function show_banner(obj) {
	if (T_Banner_List[obj.getProperty("name")] == null) {
		util.download({
			"url": BASE_URL + "outline_button.bundle",
			"success": function (res) {
				var banner_ui = gui.create(res);
				var offsetY = obj.size.y + 0.2;
				banner_ui.setObject(obj, Vector3(0, offsetY, 0));
				var occr = string.split(obj.getProperty("occurance"), " ");
				var msg = "<size=12>" + occr[1] + "\n" + obj.getProperty("name") + "</size>";
				banner_ui.setText("Button/Text", msg);
				util.downloadTexture({
					"url": BASE_URL + "demo_panel_001.png",
					"success": function (text) {
						banner_ui.setImage("Button", text);
					}
				});
				//fly to object while user click the banner
				banner_ui.regButtonEvent("Button", function () {
					fly_to_object(obj);
				});
				T_Banner_List[obj.getProperty("name")] = banner_ui;
			}
		});
	}
}

//fly to object
function fly_to_object(obj) {
	var cam_pos = camera.getEyePos();
	if (Vector3.Distance(cam_pos, obj.center) > 50) {
		camera.flyTo({
			"eye": obj.center + Vector3(0.5, 0.5, 0.5),
			"target": obj.center,
			"time": 1,
			"complete": function () {}
		});
	}
}

//react to fire alarm level
function fly_to_fire_level(fireObj) {
	var location_array = string.split(fireObj.getProperty('location'), '_')
		var building_name = location_array[0]
		var building = world.buildingList.get_Item(get_building_index_by_name(building_name));
	util.setTimeout(function () {
		level.change(building);
		util.setTimeout(function () {
			var floor_index = get_floor_by_name(building_name, fireObj.getProperty("location"))
				var floor = building.planList.get_Item(floor_index)
				level.change(floor);
		}, 100);
	}, 100);
}

function fly_to_gas_level(gasObj) {
	var location_array = string.split(gasObj.getProperty('location'), '_')
		//print(gasObj.getProperty('location'))
		var building_name = 'P2' + location_array[0]
		//print(building_name)
		var building = world.buildingList.get_Item(get_building_index_by_name(building_name));
	util.setTimeout(function () {
		level.change(building);
		util.setTimeout(function () {
			var floor_index = get_floor_by_name(building_name, gasObj.getProperty("location"))
				var floor = building.planList.get_Item(floor_index)
				level.change(floor);
		}, 100);
	}, 100);
}

//open camera live feed
function open_camera_live_feed(objId) {
	var camObj = object.find(objId);
	if (camObj != null) {
		util.setTimeout(function () {
			selector.select(camObj);
		}, 1000);
	}
}

function remove_all_gas_alarm() {
	foreach(var item in vpairs(table.keys(T_Live_Gas_Alarm))) {
		var obj = object.find(item);
		obj.setColorFlash(false);
		if (T_Banner_List[item] != null) {
			T_Banner_List[item].destroy();
			table.remove(T_Banner_List, item);
		}
		table.remove(T_Fly_List, item);
	}
}

function update_fire_alarm_table() {
	foreach(var item in vpairs(table.keys(T_Live_Fire_Alarm))) {
		if (string.length(T_Live_Fire_Alarm[item]) > 1) {
			var fireObj = object.find(item);
			fireObj.addProperty("name", item);
			var t = string.split(T_Live_Fire_Alarm[item], "|");
			fireObj.addProperty("occurance", t[0]);
			fireObj.addProperty("name", item);
			fireObj.addProperty("location", t[2]);
			util.setTimeout(function () {
				show_banner(fireObj);
				fireObj.setColorFlash(true, Color.red, 2.5);
				if (table.containskey(T_Fly_List, fireObj.getProperty("name")) == false) {
					fly_to_fire_level(fireObj);
					T_Fly_List[fireObj.getProperty("name")] = fireObj;
				}
			}, 1000);

		}
	}
}

function update_gas_alarm_table(flyObjString) {
	foreach(var item in vpairs(table.keys(T_Live_Gas_Alarm))) {
		if (string.length(T_Live_Gas_Alarm[item]) > 1) {
			var gasObj = object.find(item);
			var t = string.split(T_Live_Gas_Alarm[item], "|");
			gasObj.addProperty("location", t[2]);
			gasObj.addProperty("name", item);
			gasObj.addProperty("occurance", t[0]);
			util.setTimeout(function () {
				gasObj.setColorFlash(true, Color.red, 2.5);
				show_banner(gasObj);
				//check if have flied once and only fly to first gas sensor
				var if_fly = string.contains(flyObjString, gasObj.getProperty("name"))
				if (table.containskey(T_Fly_List, gasObj.getProperty("name")) == false && if_fly == true) {
					fly_to_gas_level(gasObj);
					T_Fly_List[gasObj.getProperty("name")] = gasObj;
				}
			}, 1000);

		}
	}
}

gui.createButton("Listen", Rect(40, 220, 60, 30), function () {
	if (LISTENING == false) {
		LISTENING = true;
		util.setInterval(function () {
			if (LISTENING) {
				//polling for fire information
				//msg format: 2017-10-16 06:23:07|F110052|P2B_2F#2017-10-16 06:23:21|F110052|P2B_2F#2017-10-16 06:23:30|F110052|P2B_2F
				util.download({
					"url": BASE_URL + "fire",
					"type": "text",
					"success": function (rs) {
						if (string.length(rs) > 10) {
							rs = string.trim(rs);
							var msgArray = string.split(rs, "#");
							for (var i = 0; i < array.count(msgArray); i++) {
								tmpArray = string.split(msgArray[i], "|");
								T_Live_Fire_Alarm[tmpArray[1]] = msgArray[i];
							}
							update_fire_alarm_table();
						}

					},
					"error": function (t) {
						print(t);
					}
				});
				//polling for gas information
				// message format: 2017-10-16 16:56:48|leak1-28|A_3F#2017-10-16 16:56:48|leak3-29|A_3F#2017-10-16 16:56:48|leak3-61|B_2F
				util.download({
					"url": BASE_URL + "gas",
					"type": "text",
					"success": function (rs) {
						if (string.length(rs) > 10) {
							rs = string.trim(rs);
							var msgArray = string.split(rs, "#");
							for (var i = 0; i < array.count(msgArray); i++) {
								var tmpArray = string.split(msgArray[i], "|");
								T_Live_Gas_Alarm[tmpArray[1]] = msgArray[i];
							}
							update_gas_alarm_table(msgArray[0]);
						} else {
							//no gas alarms, clear alarm array
							remove_all_gas_alarm();
						}
					},
					"error": function (t) {
						print(t);
					}
				});
			}
		}, 3000);
	}
});

gui.createButton("Reset", Rect(40, 260, 60, 30), function () {
	util.clearAllTimers();
	selector.ClearSelection();
	foreach(var item in vpairs(table.keys(T_Banner_List))) {
		if (T_Banner_List[item] != null) {
			T_Banner_List[item].destroy();
		}
	}
	camera.flyTo({
		"eye": Vector3(-80, 80, -50),
		"target": Vector3(3, 4, 5),
		"time": 1,
		"complete": function () {
			LISTENING = false;
			util.setTimeout(function () {
				CURRENT_LEVEL = 'world';
				level.change(world);
				table.clear(T_Banner_List);
				table.clear(T_Live_Fire_Alarm);
				table.clear(T_Fly_List);
			}, 500);
		}
	});
});
