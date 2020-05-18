from luma.core.render import canvas


class Screen:
    positions = {
        "1": (5, 5),
        "2": (5, 15),
        "3": (5, 25),
        "4": (5, 35),
        "5": (5, 45),
    }

    def __init__(self, device, fps=25):
        self.device = device
        self.fps = fps
        self.data = {
            "1": "---",
            "2": "---",
            "3": "---",
            "4": "---",
            "5": "---",
        }
    
    def draw(self):
        with canvas(self.device) as draw:
            for section, value in self.data.items():
                draw.text(self.positions[section], value, fill=1)