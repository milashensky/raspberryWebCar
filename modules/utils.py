import numpy as np
import math
import serial
import time
import pynmea2


def calculate_direction(A, B, C):
    coords = [A, B, C]
    last = coords[0]
    curr = coords[1]
    nxt = coords[2]
    m1 = curr[1] - last[1]
    n1 = curr[0] - last[0]
    m2 = nxt[1] - curr[1]
    n2 = nxt[0] - curr[0]
    D = (nxt[1] - last[1]) * (curr[0] - last[0]) - (nxt[0] - last[0]) * (curr[1] - last[1])
    # angle = math.acos((m1 * m2 + n1 * n2) / (math.sqrt(m1 * m1 + n1 * n1) * math.sqrt(m2 * m2 + n2 * n2))) * 180 / 3.15

    # D > 0 right
    # D < 0 left

    # forward or backward by distanse from last and current
    return D


def latlong_to_3d(latr, lonr):
    """Convert a point given latitude and longitude in radians to
    3-dimensional space, assuming a sphere radius of one."""
    return np.array((
        math.cos(latr) * math.cos(lonr),
        math.cos(latr) * math.sin(lonr),
        math.sin(latr)
    ))

def angle_between_vectors_degrees(u, v):
    """Return the angle between two vectors in any dimension space,
    in degrees."""
    return np.degrees(
        math.acos(np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))))

def get_angle(A, B, C):
    # Convert the points to numpy latitude/longitude radians space
    a = np.radians(np.array(A))
    b = np.radians(np.array(B))
    c = np.radians(np.array(C))

    # Vectors in latitude/longitude space
    avec = a - b
    cvec = c - b

    # Adjust vectors for changed longitude scale at given latitude into 2D space
    lat = b[0]
    avec[1] *= math.cos(lat)
    cvec[1] *= math.cos(lat)

    # Find the angle between the vectors in 2D space
    angle2deg = angle_between_vectors_degrees(avec, cvec)

    # The points in 3D space
    a3 = latlong_to_3d(*a)
    b3 = latlong_to_3d(*b)
    c3 = latlong_to_3d(*c)

    # Vectors in 3D space
    a3vec = a3 - b3
    c3vec = c3 - b3

    # Find the angle between the vectors in 2D space
    angle3deg = angle_between_vectors_degrees(a3vec, c3vec)

    return angle2deg, angle3deg


def get_distance(lat1, lon1, lat2, lon2):
    try:
        return math.fabs(6371000 * math.acos(math.cos(math.radians(float(lat1))) *
                                math.cos(math.radians(float(lat2))) *
                                math.cos(math.radians(float(lon2)) - math.radians(float(lon1))) +
                                math.sin(math.radians(float(lat1))) * math.sin(math.radians(float(lat2)))))
    except ValueError:
        return 1000000

def readlineCR(port):
    rv = ""
    while True:
        ch = ''
        try:
            ch = port.read().decode('ascii')
            rv += ch
        except UnicodeDecodeError:
            pass
        # print(rv)
        if ch=='\r' or ch=='':
            return rv
    return None


def getLocation():
    port = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=3.0)
    one = False
    msg = []
    parsed = []
    while True:
        p = readlineCR(port)
        # print('p = ', p)
        if p.strip().startswith('$GNRMC') and not one:
            one = True
        if one:
            msg.append(p);
        if p.strip().startswith('$BDGSV'):
            if len(msg) > 1:
                one = False
                parsed = [pynmea2.parse(msg[0]), pynmea2.parse(msg[1])]
                break
            else:
                msg = []
    return parsed
