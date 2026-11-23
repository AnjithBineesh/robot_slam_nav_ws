import math

from slam_sim.odometry_noise import DifferentialDriveNoiseModel


def test_zero_noise_preserves_odometry_pose():
    model = DifferentialDriveNoiseModel(0.0, 0.0, 42)
    model.update(0.0, 0.0, 0.0)

    x, y, yaw = model.update(1.0, 0.0, math.pi / 2.0)

    assert math.isclose(x, 1.0)
    assert math.isclose(y, 0.0)
    assert math.isclose(yaw, math.pi / 2.0)


def test_stationary_odometry_does_not_accumulate_noise():
    model = DifferentialDriveNoiseModel(0.1, 0.1, 42)
    first_pose = model.update(0.0, 0.0, 0.0)

    for _ in range(10):
        pose = model.update(0.0, 0.0, 0.0)

    assert pose == first_pose
    assert model.translation_variance == 0.0
    assert model.yaw_variance == 0.0


def test_noise_is_reproducible_for_same_seed():
    first = DifferentialDriveNoiseModel(0.01, 0.01, 7)
    second = DifferentialDriveNoiseModel(0.01, 0.01, 7)
    poses = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.2), (1.5, 0.5, 0.6)]

    first_results = [first.update(*pose) for pose in poses]
    second_results = [second.update(*pose) for pose in poses]

    assert first_results == second_results
