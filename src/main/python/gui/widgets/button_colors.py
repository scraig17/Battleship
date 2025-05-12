class ButtonColors:
    """
    A set of colors used in rendering buttons.

    Buttons have three states -- inactive (when the mouse isn't over the button),
    hover (when the mouse is over the button, but no mouse button is pressed),
    and active (when the mouse button is held down while the mouse is positioned
    over the button). There is a background color for each state, plus a foreground
    color for the button label, and a color for the border.
    """
    def __init__(self, fg, bg_inactive, bg_active, bg_hover, border):
        self.fg = fg
        self.bg_inactive = bg_inactive
        self.bg_active = bg_active
        self.bg_hover = bg_hover
        self.border = border
