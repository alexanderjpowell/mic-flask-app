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

const textEmail = document.getElementById("textEmail");
const textPassword = document.getElementById("textPassword");
const btnLogin = document.getElementById("btnLogin");

// Trigger login button press on enter key
textEmail.addEventListener("keyup", function(event) {
	if (event.keyCode === 13) {
		event.preventDefault();
		document.getElementById("btnLogin").click();
	}
});

textPassword.addEventListener("keyup", function(event) {
	if (event.keyCode === 13) {
		event.preventDefault();
		document.getElementById("btnLogin").click();
	}
});
//

btnLogin.addEventListener("click", e => {
	NProgress.start();
	const email = textEmail.value;
	const pass = textPassword.value;
	const auth = firebase.auth();

	//
	/*const promise = auth.setPersistence(firebase.auth.Auth.Persistence.local).then(function() {
		auth.signInWithEmailAndPassword(email, pass).then(function() {
			console.log('signed in');
			sendDataToServer(auth.currentUser.uid, email, pass);
		}).catch(function(error) {
			var errorCode = error.code;
			var errorMessage = error.message;
			console.log("errorCode: " + errorCode);
			console.log("errorMessage: " + errorMessage);
			NProgress.done();
		});
	}).catch(function(error) {
		var errorCode = error.code;
		var errorMessage = error.message;
		console.log("errorCode: " + errorCode);
		console.log("errorMessage: " + errorMessage);
		NProgress.done();
	});*/
	//

	const promise = auth.signInWithEmailAndPassword(email, pass).then(function() {
		console.log('signed in');
		sendDataToServer(auth.currentUser.uid, email, pass);
	}).catch(function(error) {
		var errorCode = error.code;
		var errorMessage = error.message;
		console.log("errorCode: " + errorCode);
		console.log("errorMessage: " + errorMessage);
		NProgress.done();
	});
});

/*error codes:
auth/invalid-email
auth/user-not-found
auth/wrong-password
*/

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

function sendDataToServer(uid, email, password) {
	var url = "/_route_to_api";
	var data = { 'uid' : uid, 'email' : email, 'password' : password };
	$.post(url, data, function() {
		window.location.href = "/";
		NProgress.done();
	});
}

function resetValues() {
	email.innerHTML = "";
	uid.innerHTML = "";
	display_name.innerHTML = "";
}

function showSigninErrors() {
	
}

//process.env.TEST_CONFIG_VAR = 'this-is-a-test';
//console.log(process.env.TEST_CONFIG_VAR);
































