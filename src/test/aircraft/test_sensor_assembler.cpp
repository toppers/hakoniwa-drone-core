#include <gtest/gtest.h>
#include <iostream>
#include "aircraft/impl/noise/sensor_noise.hpp"
#include "aircraft/impl/noise/sensor_data_assembler.hpp"

using namespace hako::aircraft;
using namespace hako::aircraft::impl;

class UtilsTest : public ::testing::Test {
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

TEST_F(UtilsTest, NoiseStatisticsTest_001) 
{
    SensorNoise noise(0.1);
    const int samples = 100;
    double sum = 0;
    double sum_squares = 0;

    for (int i = 0; i < samples; ++i) {
        double noise_value = noise.add_random_noise(0);
        sum += noise_value;
        sum_squares += noise_value * noise_value;
    }

    double mean = sum / samples;
    double variance = sum_squares / samples - mean * mean;

    EXPECT_NEAR(0, mean, 0.05);
    EXPECT_NEAR(0.05, variance, 0.05);
}
TEST_F(UtilsTest, SensorDataAssemblerTest_001)
{
    SensorDataAssembler obj(3);
    EXPECT_EQ(0, obj.get_calculated_value());
    EXPECT_EQ(0, obj.size());
}
TEST_F(UtilsTest, SensorDataAssemblerTest_002)
{
    SensorDataAssembler obj(3);
    obj.add_data(1);
    EXPECT_EQ(1, obj.get_calculated_value());
    EXPECT_EQ(1, obj.size());
}
TEST_F(UtilsTest, SensorDataAssemblerTest_003)
{
    SensorDataAssembler obj(3);
    obj.add_data(1);
    obj.add_data(2);
    EXPECT_EQ(1.5, obj.get_calculated_value());
}
TEST_F(UtilsTest, SensorDataAssemblerTest_004)
{
    SensorDataAssembler obj(3);
    obj.add_data(1);
    obj.add_data(2);
    obj.add_data(3);
    EXPECT_EQ(2, obj.get_calculated_value());
}
TEST_F(UtilsTest, SensorDataAssemblerTest_005)
{
    SensorDataAssembler obj(3);
    obj.add_data(1);
    obj.add_data(2);
    obj.add_data(3);
    obj.add_data(4);
    EXPECT_EQ(3, obj.get_calculated_value());
}
TEST_F(UtilsTest, SensorDataAssemblerTest_006)
{
    SensorDataAssembler obj(3);
    obj.add_data(1);
    obj.add_data(2);
    obj.add_data(3);
    obj.add_data(4);
    EXPECT_EQ(3, obj.get_calculated_value());
    obj.reset();
    EXPECT_EQ(0, obj.size());
}