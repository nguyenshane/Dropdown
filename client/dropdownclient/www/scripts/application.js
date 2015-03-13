/*angular.module('SteroidsApplication', [
  'supersonic'
])
.controller('IndexController', function($scope, supersonic) {

  $scope.navbarTitle = "Welcome to Supersonic!";

});
*/

var db = $.db("dropdown", "", "Dropdown Database", 1024 * 1024);
db.createTable({
	name: "users",
	columns: [
	  "id INTEGER PRIMARY KEY",
	  "first_name TEXT",
	  "last_name INTEGER",
	  "point INTEGER",
	  "photo_url TEXT"
	],
	dropOrIgnore: "ignore", 
	done: function () {
	  console.log("Created users database");
	},
	fail: function () {
	  console.log("Something went wrong....");
	}
});


function getAuth(){
  return btoa(JSON.parse(localStorage.getItem("email")) + ':' +
              JSON.parse(localStorage.getItem("password")));
}

function fail(e){
  console.log('error', e);
}

function show_user(userarray, fromnum){
	if(userarray.length <= fromnum){
		var tonum = fromnum+5;
		var param = 'fromnum='+fromnum+'&tonum='+tonum;
		var self = this;
		$.ajax({
			url: 'http://dropdown.nguyenshane.com/dropdown/default/api/show_user.json',
			headers: { 'X-Requested-With': 'XMLHttpRequest',
			          'Authorization': 'Basic ' + getAuth(), },
			data: param,
			dataType: 'json',
			cache: false,
			contentType: false,
			processData: false,
			type: 'GET',
			success: function(response){
			  console.log('show_user', response, userarray);
			  add_user_to_database(userarray, response.result)
			}
		});
	}
}

function add_user_to_database(userarray, response){
	console.log('response', response);
	//var userarray = [];
	for (var user in response){
		var id = response[user].auth_user.id;
		var first_name = response[user].auth_user.first_name;
		var last_name = response[user].auth_user.last_name;
		var point = response[user].auth_user.point;
		var photo_url = response[user].user_photo.cached_url;
		if(photo_url == null){
			photo_url = "/images/noavatar.png";
		}

		db.insert("users", {
            data: {
                id: id,
                first_name: first_name,
                last_name: last_name,
                point: point,
                photo_url: photo_url
            },
            done: function () {
                console.log("Created a users!");
            },
            fail: function () {
                console.log("Something went wrong....");
            }
	    });

		userarray.push({id: id, photo_url:photo_url, last_name:last_name, first_name:first_name, point:point});

		/*
		if(user == response.length-1){
			scope.$.threshold.clearLower();
			//return userarray;
		}*/
	}
}


function show_friends(userarray, fromnum){
	if(userarray.length == 0){
		var tonum = fromnum+100;
		var param = 'fromnum='+fromnum+'&tonum='+tonum;
		var self = this;
		$.ajax({
			url: 'http://dropdown.nguyenshane.com/dropdown/default/api/show_friends.json',
			headers: { 'X-Requested-With': 'XMLHttpRequest',
			          'Authorization': 'Basic ' + getAuth(), },
			dataType: 'json',
			cache: false,
			contentType: false,
			processData: false,
			type: 'GET',
			success: function(response){
			  console.log('show_friends', response, userarray);
			  add_friend_to_database(userarray, response.result)
			}
		});
	}
}

function fake_random_array(){
	var total = Math.floor((Math.random() * 3) + 0);
	var array = [];
	for (var i=0; i<total; i++){
		array.push(Math.floor((Math.random() * 10) + 0));
	}
	return array;
}

function findById(source, id) {
    return source.filter(function(obj) {
        // for val & type comparison
        return +obj.id === +id;
    })[ 0 ];
}

function add_friend_to_database(userarray, response){
	console.log('response', response);
	//var userarray = [];
	for (var user in response){
		var id = response[user].auth_user.id;
		var first_name = response[user].auth_user.first_name;
		var last_name = response[user].auth_user.last_name;
		var point = response[user].auth_user.point;
		var photo_url = response[user].user_photo.cached_url;
		var throwdown = fake_random_array(); //response[user].throwdown;
		var dropdown = fake_random_array();//response[user].dropdown;

		if(photo_url == null){
			photo_url = "/images/noavatar.png";
		}

		db.insert("users", {
            data: {
                id: id,
                first_name: first_name,
                last_name: last_name,
                point: point,
                photo_url: photo_url
            },
            done: function () {
                console.log("Created a users!");
            },
            fail: function () {
                console.log("Something went wrong....");
            }
	    });

		userarray.push({id: id, photo_url:photo_url, last_name:last_name, first_name:first_name, 
			point:point, throwdown: throwdown, dropdown: dropdown});

		/*
		if(user == response.length-1){
			scope.$.threshold.clearLower();
			//return userarray;
		}*/
	}
}


function dataURItoBlob(dataURI) {
	// convert base64/URLEncoded data component to raw binary data held in a string
	var byteString;
	if (dataURI.split(',')[0].indexOf('base64') >= 0)
	    byteString = atob(dataURI.split(',')[1]);
	else
	    byteString = unescape(dataURI.split(',')[1]);

	// separate out the mime component
	var mimeString = dataURI.split(',')[0].split(':')[1].split(';')[0];

	// write the bytes of the string to a typed array
	var ia = new Uint8Array(byteString.length);
	for (var i = 0; i < byteString.length; i++) {
	    ia[i] = byteString.charCodeAt(i);
	}
	return new Blob([ia], {type:mimeString});
}