style_application = """

* {
border: none;
}

#new_tab {
    min-width: 40px;
    min-height: 10px;

}

QTabBar::tab {
    border: 0px solid #fff;
    border-radius: 10px;
    margin: 3px;
    padding: 3px;
}

QTabBar::close-button {
    image: url(images/close-white.png);
    width: 25px;
    height: 25px;
    margin: 2px 0 0 2px;
}

QTabBar::tab:selected {
    background-color: white;
    color: black;
}

QTabBar::tab:!selected {
    background-color: #4F4659;
    color: white;
}
"""