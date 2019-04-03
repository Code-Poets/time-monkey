function displayNav() {
 text_div_styles = document.getElementsByClassName("text");
 menu_styles = document.getElementById("menu").style;
 user_type_div_styles = document.getElementById("user-type").style;
 sheetstorm_div_styles = document.getElementById("sheetstorm").style;
 avatar_div_styles = document.getElementById("avatar").style;
if (menu_styles.width == "15%" || menu_styles.width == "") {
    user_type_div_styles.visibility = "hidden";
    menu_styles.width = "8%";
    sheetstorm_div_styles.display = "none";
    avatar_div_styles.marginLeft = "-2.1rem";
    for (i = 0; i < text_div_styles.length; i++) {
        text_div_styles[i].style.display = "none";
    }
} else {
    menu_styles.width = "15%";
    user_type_div_styles.visibility = "visible";
    sheetstorm_div_styles.display = "inline-block";
    avatar_div_styles.marginLeft = "0";
    for (i = 0; i < text_div_styles.length; i++) {
        text_div_styles[i].style.display = "block";
    }
  }
}