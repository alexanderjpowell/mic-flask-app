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
const changePasswordButton = document.getElementById("change-password-button");
const cancelButton = document.getElementById("cancel-button");

const alertSuccess = document.getElementById("alert-success");
const alertError = document.getElementById("alert-error");

firebase.initializeApp(firebaseConfig);

var user = firebase.auth().currentUser;

firebase.auth().onAuthStateChanged((firebaseUser) => {
	console.log("AuthStateChanged");
	if (firebaseUser) {
		console.log("User logged in: " + firebaseUser);
		user = firebaseUser;
	} else {
		console.log("user not logged in");
	}
});

changePasswordButton.addEventListener("click", e => {
	let currentpasswordinput = document.getElementById('current-password-input').value;
	let newpasswordinput = document.getElementById('new-password-input').value;
	let confirmpasswordinput = document.getElementById('confirm-password-input').value;

	if ((currentpasswordinput == "") || (newpasswordinput == "") || (confirmpasswordinput == "")) {
		alert('Enter all values');
		return;
	}
	if (newpasswordinput != confirmpasswordinput) {
		alert('New passwords must match');
		return;
	}

	const credential = firebase.auth.EmailAuthProvider.credential(user.email, currentpasswordinput);

	user.reauthenticateWithCredential(credential).then(function() {
		user.updatePassword(confirmpasswordinput).then(function() {
			//alert('password change successful');
			alertSuccess.style.display = "block";
			alertError.style.display = "none";
			currentpasswordinput = "";
			newpasswordinput = "";
			confirmpasswordinput = "";
		}).catch(function(error) {
			//alert(error);
			alertSuccess.style.display = "none";
			alertError.style.display = "block";
		});
	}).catch(function(error) {
		alertSuccess.style.display = "none";
		alertError.style.display = "block";
	});
});

function resetInputs() {
	document.getElementById('current-password-input').value = "";
	document.getElementById('new-password-input').value = "";
	document.getElementById('confirm-password-input').value = "";
}

cancelButton.addEventListener("click", e => {
	document.location.href = "/account";
});

