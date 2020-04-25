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

firebase.auth().onAuthStateChanged((firebaseUser) => {
	console.log("AuthStateChanged");
	if (firebaseUser) {
		console.log("User logged in: " + firebaseUser);
	} else {
		console.log("user not logged in");
	}
});

/*if (user != null) {
	console.log('email ' + user.email)
	console.log('displayName ' + user.displayName)
	emailText.innerHTML = user.email;
	nameText.innerHTML = user.displayName;
} else {
	console.log('user is null');
}*/







































































































































































