var firebaseConfigDebug = {
	apiKey: "AIzaSyChpix6yjeK8mCgiQ2cfOy4iwfVGltGAko",
    authDomain: "ml-kit-codelab-f80ef.firebaseapp.com",
    databaseURL: "https://ml-kit-codelab-f80ef.firebaseio.com",
    storageBucket: "ml-kit-codelab-f80ef.appspot.com",
};

var firebaseConfig = {
	apiKey: "AIzaSyDYnjnjYFi-Cvq2f55hjYTXnqSUhJxZbyM",
    authDomain: "meter-image-capturing.firebaseapp.com",
    databaseURL: "https://meter-image-capturing.firebaseio.com",
    storageBucket: "meter-image-capturing.appspot.com",
};

firebase.initializeApp(firebaseConfig);

const btnLogout = document.getElementById("btnLogout");
const btnDownloadReport = document.getElementById("btnDownloadReport");
const btnNewRecord = document.getElementById('btnNewRecord');
const btnSubmitNewRecord = document.getElementById("btnSubmitNewRecord");

const machine_id = document.getElementById("machine_id");
const progressive1 = document.getElementById("progressive1");
const progressive2 = document.getElementById("progressive2");
const progressive3 = document.getElementById("progressive3");
const progressive4 = document.getElementById("progressive4");
const progressive5 = document.getElementById("progressive5");
const progressive6 = document.getElementById("progressive6");
const progressive7 = document.getElementById("progressive7");
const progressive8 = document.getElementById("progressive8");
const progressive9 = document.getElementById("progressive9");
const progressive10 = document.getElementById("progressive10");
const notes = document.getElementById("notes");
const user = document.getElementById("userName");

const dataTableDiv = document.getElementById("dataTableDiv");
const emptyStateDiv = document.getElementById("emptyStateDiv");

const casino_li = document.getElementById("casino-li");
//const adminButton = document.getElementById("admin-mode-button");
const casino_select = document.getElementById("casino-select");

dataTableDiv.style.display = "none";
emptyStateDiv.style.display = "block";

firebase.auth().onAuthStateChanged((firebaseUser) => {
	console.log("AuthStateChanged");
	if (firebaseUser) {
		console.log("User logged in: " + firebaseUser);
	} else {
		console.log("user not logged in");
	}
});

/*function initApp() {
	firebase.auth().onAuthStateChanged(firebaseUser => {
		console.log("AuthStateChanged");
		if (firebaseUser) {
			console.log("User logged in: " + firebaseUser);
			sendDataToServer(firebaseUser.uid);
		} else {
			console.log("user logged out");
		}
	});
}

window.onload = function() {
	initApp();
};*/

btnLogout.addEventListener("click", e => {
	firebase.auth().signOut().then(function() {
		console.log("user logged out");
		sendLogoutDataToServer("");
	}).catch(function(error) {
		console.log(error.message);
	});
});

btnDownloadReport.addEventListener("click", e => {
	getDataFromServer();
});

btnSubmitNewRecord.addEventListener("click", e => {
	var forms = document.getElementsByClassName("needs-validation");
	var validation = Array.prototype.filter.call(forms, function(form) {
		form.addEventListener("submit", function(event) {
			if ((form.checkValidity() === false)) {
				event.preventDefault();
				event.stopPropagation();
			}
			form.classList.add('was-validated');
		}, false);
	});
}, false);

function getAccountInfo() {
	$.post('/_send_account_info', function(data, status) {
		if (data.isAdmin) {
			for (let i = 0; i < data.casinos.length; i++) {
				casino_select.options[casino_select.options.length] = new Option(data.casinos[i].name, data.casinos[i].uid);
			}
			casino_li.style.display = "block";
			//adminButton.style.display = "block";
			btnNewRecord.style.display = "none";
		} else {
			casino_li.style.display = "none";
			//adminButton.style.display = "none";
			btnNewRecord.style.display = "block";
		}
	});
}

getAccountInfo();

function sendLogoutDataToServer(uid) {
	var url = "/_logout";
	var data = { 'uid' : uid };
	$.post(url, data, function() {
		window.location.href = "/";
	});
}

function downloadReport(csv) {
	var hiddenElement = document.createElement('a');
	hiddenElement.href = "data:text/csv;charset=utf-8," + encodeURI(csv);
	hiddenElement.target = "_blank";
	hiddenElement.download = "report.csv";
	hiddenElement.click();
}

$('.table > tbody > tr').click(function() {
	console.log($(this).index());
});

function insertRow(index, machine_id, progressive_1, progressive_2, progressive_3, progressive_4, progressive_5, progressive_6, progressive_7, progressive_8, progressive_9, progressive_10, notes, timestamp, user) {
	var index_row = '<th scope="row">' + index + '</th>';
	var machine_id_row = "<td>" + machine_id + "</td>";
	
	if (typeof progressive_1 === 'undefined') {
		progressive_1 = "";
	}
	if (typeof progressive_2 === 'undefined') {
		progressive_2 = "";
	}
	if (typeof progressive_3 === 'undefined') {
		progressive_3 = "";
	}
	if (typeof progressive_4 === 'undefined') {
		progressive_4 = "";
	}
	if (typeof progressive_5 === 'undefined') {
		progressive_5 = "";
	}
	if (typeof progressive_6 === 'undefined') {
		progressive_6 = "";
	}
	if (typeof progressive_7 === 'undefined') {
		progressive_7 = "";
	}
	if (typeof progressive_8 === 'undefined') {
		progressive_8 = "";
	}
	if (typeof progressive_9 === 'undefined') {
		progressive_9 = "";
	}
	if (typeof progressive_10 === 'undefined') {
		progressive_10 = "";
	}
	if (typeof notes === 'undefined') {
		notes = "";
	}

	let extra_headers = document.getElementById("extra-progressive-headers");
	let table_header = document.getElementById("table-header");
	
	var progressive_1_row = (progressive_1.trim() === "") ? "<td>-</td>" : "<td><font color='green'>$" + progressive_1 + "</font></td>";
	var progressive_2_row = (progressive_2.trim() === "") ? "<td>-</td>" : "<td><font color='green'>$" + progressive_2 + "</font></td>";
	var progressive_3_row = (progressive_3.trim() === "") ? "<td>-</td>" : "<td><font color='green'>$" + progressive_3 + "</font></td>";
	var progressive_4_row = (progressive_4.trim() === "") ? "<td>-</td>" : "<td><font color='green'>$" + progressive_4 + "</font></td>";
	var progressive_5_row = (progressive_5.trim() === "") ? "<td>-</td>" : "<td><font color='green'>$" + progressive_5 + "</font></td>";
	var progressive_6_row = (progressive_6.trim() === "") ? "<td>-</td>" : "<td><font color='green'>$" + progressive_6 + "</font></td>";
	var progressive_7_row = (progressive_7.trim() === "") ? "<td>-</td>" : "<td><font color='green'>$" + progressive_7 + "</font></td>";
	var progressive_8_row = (progressive_8.trim() === "") ? "<td>-</td>" : "<td><font color='green'>$" + progressive_8 + "</font></td>";
	var progressive_9_row = (progressive_9.trim() === "") ? "<td>-</td>" : "<td><font color='green'>$" + progressive_9 + "</font></td>";
	var progressive_10_row = (progressive_10.trim() === "") ? "<td>-</td>" : "<td><font color='green'>$" + progressive_10 + "</font></td>";

	var notes_row = (notes.trim() === "") ? "<td>-</td>" : "<td>" + notes + "</td>";
	var timestamp_row = "<td>" + timestamp + "</td>";
	var user_row = "<td>" + user + "</td>";
	var row_html = "";
	if ((progressive_7.trim() === "") && (progressive_8.trim() === "") && (progressive_9.trim() === "") && (progressive_10.trim() === "")) {
		row_html = "<tr>" + index_row + machine_id_row + progressive_1_row + progressive_2_row + progressive_3_row + progressive_4_row + progressive_5_row + progressive_6_row + notes_row + timestamp_row + user_row + "</tr>";
		//extra_headers.style.display = "none";
		table_header.innerHTML = '<th scope="col">#</th>' +
						'<th scope="col">ID</th>' +
						'<th scope="col">Progressive 1</th>' +
						'<th scope="col">Progressive 2</th>' +
						'<th scope="col">Progressive 3</th>' +
						'<th scope="col">Progressive 4</th>' +
						'<th scope="col">Progressive 5</th>' +
						'<th scope="col">Progressive 6</th>' +
						'<th scope="col">Notes</th>' +
						'<th scope="col">Timestamp</th>' +
						'<th scope="col">User</th>';
	} else { // Show additional column headers
		row_html = "<tr>" + index_row + machine_id_row + progressive_1_row + progressive_2_row + progressive_3_row + progressive_4_row + progressive_5_row + progressive_6_row + progressive_7_row + progressive_8_row + progressive_9_row + progressive_10_row + notes_row + timestamp_row + user_row + "</tr>";
		table_header.innerHTML = '<th scope="col">#</th>' +
						'<th scope="col">ID</th>' +
						'<th scope="col">Progressive 1</th>' +
						'<th scope="col">Progressive 2</th>' +
						'<th scope="col">Progressive 3</th>' +
						'<th scope="col">Progressive 4</th>' +
						'<th scope="col">Progressive 5</th>' +
						'<th scope="col">Progressive 6</th>' +
						'<th scope="col">Progressive 7</th>' +
						'<th scope="col">Progressive 8</th>' +
						'<th scope="col">Progressive 9</th>' +
						'<th scope="col">Progressive 10</th>' +
						'<th scope="col">Notes</th>' +
						'<th scope="col">Timestamp</th>' +
						'<th scope="col">User</th>';
	}
	$(dataTable).find('tbody').append(row_html);
}

function getDataFromServer() {
	if (casino_select.options.length == 0) {
		NProgress.start();
		$.post('/api', function(data, status) {
			downloadReport(data);
			NProgress.done();
		});
	} else {
		NProgress.start();
		var uid = { 'uid' : casino_select.options[casino_select.selectedIndex].value };
		$.post('/api', uid, function(data) {
			downloadReport(data);
			NProgress.done();
		});
	}
}

function sendDateToServer(startDate, endDate, uid=0) {
	if (uid == 0) { // Fetching data as a low level casino account user
		NProgress.start();
		var url = "/_apiii";
		var data = { 'startDate' : startDate, 'endDate' : endDate, 'timeZoneOffset' : getTimeZoneOffset() };
		$("#tableBody").empty();
		$.post(url, data, function(dataa) {
			for (var i = 0; i < dataa.length; i++) {
				insertRow(dataa[i].index, 
					dataa[i].machine_id, 
					dataa[i].progressive1, 
					dataa[i].progressive2, 
					dataa[i].progressive3, 
					dataa[i].progressive4, 
					dataa[i].progressive5, 
					dataa[i].progressive6, 
					dataa[i].progressive7, 
					dataa[i].progressive8, 
					dataa[i].progressive9, 
					dataa[i].progressive10, 
					dataa[i].notes, 
					dataa[i].timestamp, 
					dataa[i].userName);
			}
			toggleEmptyState(false)
			NProgress.done();
		});
	} else { // Fetching data as an admin to view multiple casino data
		NProgress.start();
		var url = "/_apiii";
		var data = { 'startDate' : startDate, 'endDate' : endDate, 'timeZoneOffset' : getTimeZoneOffset(), 'uid' : uid };
		$("#tableBody").empty();
		$.post(url, data, function(dataa) {
			for (var i = 0; i < dataa.length; i++) {
				insertRow(dataa[i].index, 
					dataa[i].machine_id, 
					dataa[i].progressive1, 
					dataa[i].progressive2, 
					dataa[i].progressive3, 
					dataa[i].progressive4, 
					dataa[i].progressive5, 
					dataa[i].progressive6, 
					dataa[i].progressive7, 
					dataa[i].progressive8, 
					dataa[i].progressive9, 
					dataa[i].progressive10, 
					dataa[i].notes, 
					dataa[i].timestamp, 
					dataa[i].userName);
			}
			toggleEmptyState(false)
			NProgress.done();
		});
	}
}

function toggleEmptyState(isEmpty) {
	if (isEmpty) {
		dataTableDiv.style.display = "none";
		emptyStateDiv.style.display = "block";
	} else {
		dataTableDiv.style.display = "block";
		emptyStateDiv.style.display = "none";
	}
}

//returns 4 in VA, 7 in Nevada
function getTimeZoneOffset() {
	var d = new Date();
	return d.getTimezoneOffset() / 60;
}

$("#casinos-dropdown a").click(function(e) {
	e.preventDefault(); // cancel the link behaviour
	var selText = $(this).text();

	$("#casinos-button").text(selText);
	console.log(selText + ' was chosen');
});

