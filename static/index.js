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
const btnSubmitNewRecord = document.getElementById("btnSubmitNewRecord");
//const btnLoadNewRecords = document.getElementById("btnLoadNewRecords");
const progressive_1 = document.getElementById("progressive_1");
const dataTableDiv = document.getElementById("dataTableDiv");
const emptyStateDiv = document.getElementById("emptyStateDiv");

dataTableDiv.style.display = "none";
emptyStateDiv.style.display = "block";

/*firebase.auth().onAuthStateChanged(firebaseUser => {
	console.log("AuthStateChanged");
	if (firebaseUser) {
		console.log("User logged in: " + firebaseUser);
	} else {
		console.log("user logged out");
		sendDataToServer("");
		window.location.href = "/";
	}
});*/

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
			if (form.checkValidity() === false) {
				customValidation();
				event.preventDefault();
				event.stopPropagation();
			}
			console.log(form);
			form.classList.add('was-validated');
		}, false);
	});
}, false);

/*btnLoadNewRecords.addEventListener("click", e => {
	NProgress.start();
	$.post('/_fetch_more_records', function(data, status) {
		for (var i = 0; i < data.length; i++) {
			insertRow(data[i].index, 
				data[i].machine_id, 
				data[i].progressive_1, 
				data[i].progressive_2, 
				data[i].progressive_3, 
				data[i].progressive_4, 
				data[i].progressive_5, 
				data[i].progressive_6, 
				data[i].notes, 
				data[i].timestamp, 
				data[i].user);
		}
		NProgress.done();
	});
}, false);*/

function customValidation() {
	if (progressive_1.value.includes('$')) {
		console.log('invalid');
		return false;
	} else {
		console.log('valid');
		return true;
	}
}

function sendLogoutDataToServer(uid) {
	var url = "/_logout";
	var data = { 'uid' : uid };
	$.post(url, data, function() {
		window.location.href = "/";
	});
}

function getDataFromServer() {
	NProgress.start();
	$.post('/api', function(data, status) {
		downloadReport(data);
		NProgress.done();
	});
}

function downloadReport(csv) {
	var hiddenElement = document.createElement('a');
	hiddenElement.href = "data:text/csv;charset=utf-8," + encodeURI(csv);
	hiddenElement.target = "_blank";
	hiddenElement.download = "report.txt";
	hiddenElement.click();
}

$('.table > tbody > tr').click(function() {
	console.log($(this).index());
});

function insertRow(index, machine_id, progressive_1, progressive_2, progressive_3, progressive_4, progressive_5, progressive_6, notes, timestamp, user) {
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
	if (typeof notes === 'undefined') {
		notes = "";
	}
	
	var progressive_1_row = (progressive_1.trim() === "") ? "<td>-</td>" : "<td><font color='green'>$" + progressive_1 + "</font></td>";
	var progressive_2_row = (progressive_2.trim() === "") ? "<td>-</td>" : "<td><font color='green'>$" + progressive_2 + "</font></td>";
	var progressive_3_row = (progressive_3.trim() === "") ? "<td>-</td>" : "<td><font color='green'>$" + progressive_3 + "</font></td>";
	var progressive_4_row = (progressive_4.trim() === "") ? "<td>-</td>" : "<td><font color='green'>$" + progressive_4 + "</font></td>";
	var progressive_5_row = (progressive_5.trim() === "") ? "<td>-</td>" : "<td><font color='green'>$" + progressive_5 + "</font></td>";
	var progressive_6_row = (progressive_6.trim() === "") ? "<td>-</td>" : "<td><font color='green'>$" + progressive_6 + "</font></td>";
	var notes_row = (notes.trim() === "") ? "<td>-</td>" : "<td>" + notes + "</td>";
	var timestamp_row = "<td>" + timestamp + "</td>";
	var user_row = "<td>" + user + "</td>";
	var row_html = "<tr>" + index_row + machine_id_row + progressive_1_row + progressive_2_row + progressive_3_row + progressive_4_row + progressive_5_row + progressive_6_row + notes_row + timestamp_row + user_row + "</tr>";
	$(dataTable).find('tbody').append(row_html);
}

function sendDateToServer(startDate, endDate) {
	NProgress.start();
	var url = "/_apiii";
	var data = { 'startDate' : startDate, 'endDate' : endDate };
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
				dataa[i].notes, 
				dataa[i].timestamp, 
				dataa[i].userName);
		}
		toggleEmptyState(false)
		NProgress.done();
	});
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

/*$(window).scroll(function() {
	if($(window).scrollTop() == $(document).height() - $(window).height()) {
		// ajax call get data from server and append to the div
		console.log('bottom of page');
	}
});*/

/*function getConfigVarsFromServer() {
	$.post('/config', function(data, status) {
		console.log(data);
	});
}

process.env.TEST_CONFIG_VAR = 'this-is-a-test';
console.log(process.env.TEST_CONFIG_VAR);*/

