import common_use_modules as cum
import frontend

if __name__ == '__main__':
    data = cum.read_gps("recordings_1/636019921_fajny.gps")
    gps_route = [[float(x[0]), float(x[1])] for x in data]
    frontend.draw_map(gps_route, None, None)