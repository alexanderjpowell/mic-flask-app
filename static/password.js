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

const emailText = document.getElementById("emailText");
const nameText = document.getElementById("nameText");

firebase.initializeApp(firebaseConfig);

var user = firebase.auth().currentUser;

function changePassword() {
				let currentpasswordinput = document.getElementById('current-password-input').value;
				let newpasswordinput = document.getElementById('new-password-input').value;
				let confirmpasswordinput = document.getElementById('confirm-password-input').value;

				if ((currentpasswordinput == "") || (newpasswordinput == "") || (confirmpasswordinput == "")) {
					alert('Enter all values');
					return false;
				}
				if (newpasswordinput != confirmpasswordinput) {
					alert('New passwords must match');
					return false;
				}
				user.reauthenticateWithCredential(currentpasswordinput).then(function() {
					alert('successful');
					return false;
				}).catch(function(error) {
					alert(error);
					return false;
				});
			}

/*function changePassword() {
	let currentpasswordinput = document.changepasswordform.currentpasswordinput.value;
	let newpasswordinput = document.changepasswordform.newpasswordinput.value;
	let confirmpasswordinput = document.changepasswordform.confirmpasswordinput.value;
	if ((currentpasswordinput == "") || (newpasswordinput == "") || (confirmpasswordinput == "")) {
		alert('Enter all values');
		return false;
	}
	if (newpasswordinput != confirmpasswordinput) {
		alert('New passwords must match');
		return false;
	}
	return true;

	// Check if given password is valid
	user.reauthenticateWithCredential(currentpasswordinput).then(function() {
		// User re-authenticated. Now update password
		//user.updatePassword(confirmpasswordinput).then(function() {
			// Update successful.
		//	return true;
		//}).catch(function(error) {
			// An error happened.
		//	alert(error);
		//	return false;
		//});
		alert('successful');
		return false;
	}).catch(function(error) {
		// An error happened.
		alert('Incorrect Password');
		return false;
	});
}*/

