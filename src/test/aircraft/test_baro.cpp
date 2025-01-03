#include <gtest/gtest.h>
#include <iostream>
#include "aircraft/impl/sensors/sensor_baro.hpp"
#include "aircraft/impl/noise/sensor_noise.hpp"

using namespace hako::aircraft;
using namespace hako::aircraft::impl;
using namespace hako::logger;

class BaroTest : public ::testing::Test {
protected:
    static void SetUpTestCase()
    {
    }
    static void TearDownTestCase()
    {
    }
    virtual void SetUp()
    {
    }
    virtual void TearDown()
    {
    }

};


TEST_F(BaroTest, SensorBaro_001) 
{
    SensorBaro baro(0.001, 3);
    DronePositionType value;
    value.data.x = 1;
    value.data.y = 2;
    value.data.z = 3;
    baro.run(value);
    value.data.x = 2;
    value.data.y = 3;
    value.data.z = 4;
    baro.run(value);
    value.data.x = 3;
    value.data.y = 4;
    value.data.z = 5;
    baro.run(value);

    DroneBarometricPressureType result = baro.sensor_value();

    //EXPECT_EQ(10, result.abs_pressure);
    EXPECT_EQ(0, result.diff_pressure);
    EXPECT_EQ(-4, result.pressure_alt);
}

TEST_F(BaroTest, SensorBaro_002) 
{
    SensorBaro baro(0.001, 3);
    SensorNoise noise(0.01);
    baro.set_noise(&noise);
    DronePositionType value;
    value.data.x = 1;
    value.data.y = 2;
    value.data.z = 3;
    baro.run(value);
    value.data.x = 2;
    value.data.y = 3;
    value.data.z = 4;
    baro.run(value);
    value.data.x = 3;
    value.data.y = 4;
    value.data.z = 5;
    baro.run(value);

    DroneBarometricPressureType result = baro.sensor_value();

    //EXPECT_GT(result.abs_pressure, 10-0.02);
    //EXPECT_LT(result.abs_pressure, 10+0.02);

    EXPECT_GT(result.diff_pressure, -0.05);
    EXPECT_LT(result.diff_pressure, 0.05);

    EXPECT_GT(result.pressure_alt, -4 -0.05);
    EXPECT_LT(result.pressure_alt, -4 + 0.05);
}
