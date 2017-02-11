
// Insert HTML code into editor text area.
function addCode(code) {
	document.forms["editor"]["content"].value = 
		document.forms["editor"]["content"].value += code;
	document.forms["editor"]["content"].focus();
}

// Check form to avoid empty values and bad email.
function checkSignup() {
	if(document.forms["signup"]["name"].value == "")
    {
        alert("Please enter your real name");
        document.forms["signup"]["name"].focus();
        return false;
    }
    if(document.forms["signup"]["user"].value == "")
    {
        alert("Please fill in your user name");
        document.forms["signup"]["user"].focus();
        return false;
    }
	var x=document.forms["signup"]["mail"].value;
	var atpos=x.indexOf("@");
	var dotpos=x.lastIndexOf(".");
	if (atpos<1 || dotpos<atpos+2 || dotpos+2>=x.length)
	{
		alert("Missing or not a valid email address");
		return false;
	}
}

// Check for empty messages on Community Wall
function checkWall() {
	if(document.forms["wall"]["message"].value == "")
    {
        alert("Empty message box :-) Write down and then press ENTER");
        document.forms["signup"]["message"].focus();
        return false;
    }
}
