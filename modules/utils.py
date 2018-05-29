import numpy as np
import math


def calculateDirection():
    coords = [[55.771666, 37.576287], [55.772159, 37.576265], [55.772956, 37.574639]]
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
    return True


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
