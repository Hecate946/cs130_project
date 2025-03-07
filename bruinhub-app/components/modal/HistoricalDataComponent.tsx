import React from 'react';
import { View, Text, StyleSheet, Dimensions, ScrollView } from 'react-native';
import { BarChart } from 'react-native-chart-kit';

// Define types for our data structure
type OccupancyItem = {
  capacity: number;
  occupants: number;
};

type OccupancyData = {
  [key: string]: OccupancyItem;
};

// Component props
interface HistoricalDataComponentProps {
  data: OccupancyData;
}

export default function HistoricalDataComponent({ data }: HistoricalDataComponentProps) {
  // Format time labels (e.g. 13 -> 1 PM, 25 -> 1 AM)
  const formatTimeLabel = (hour: string): string => {
    const numHour = parseInt(hour);

    if (numHour === 24) return '12 AM';
    if (numHour === 25) return '1 AM';
    if (numHour === 12) return '12 PM';
    if (numHour > 12) return `${numHour - 12} PM`;
    return `${numHour} AM`;
  };

  // Process data for the chart
  const processData = () => {
    return Object.keys(data)
      .sort((a, b) => parseInt(a) - parseInt(b))
      .map(hour => {
        const { capacity, occupants } = data[hour];
        const occupancyPercentage = capacity > 0
          ? Math.round((occupants / capacity) * 100)
          : 0;

        return {
          hour,
          displayHour: formatTimeLabel(hour),
          percentage: occupancyPercentage,
          rawOccupants: occupants,
          rawCapacity: capacity
        };
      });
  };

  const chartData = processData();
  const screenWidth = Dimensions.get('window').width - 20;

  // Calculate statistics
  const validData = chartData.filter(item => item.rawCapacity > 0);
  const highestOccupancy = validData.reduce(
    (max, current) => current.percentage > max.percentage ? current : max,
    { displayHour: '', percentage: 0 }
  );
  const lowestOccupancy = validData.reduce(
    (min, current) => current.percentage < min.percentage ? current : min,
    { displayHour: '', percentage: 100 }
  );
  const avgOccupancy = validData.length > 0
    ? Math.round(validData.reduce((sum, item) => sum + item.percentage, 0) / validData.length)
    : 0;

  // Get color based on occupancy percentage
  const getOccupancyColor = (percentage: number) => {
    if (percentage >= 80) return '#eb5757'; // Red
    if (percentage >= 50) return '#f2994a'; // Orange
    return '#48a672'; // Green
  };

  // Max bar width
  const maxBarWidth = screenWidth * 0.65;

  return (
    <View>
      <Text style={styles.title}>Historical Capacity</Text>
      <View style={styles.container}>
        <ScrollView 
          style={styles.chartContainer}
          showsVerticalScrollIndicator={false}
        >
          {chartData.map((item, index) => (
            <View key={index} style={styles.barRow}>
              <Text style={styles.timeLabel}>{item.displayHour}</Text>
              <View style={styles.barContainer}>
                <View
                  style={[
                    styles.bar,
                    {
                      width: (item.percentage / 100) * maxBarWidth,
                      backgroundColor: getOccupancyColor(item.percentage)
                    }
                  ]}
                />
                <Text style={styles.percentageLabel}>{item.percentage}%</Text>
              </View>
            </View>
          ))}
        </ScrollView>

        <View style={styles.statsContainer}>
          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Peak</Text>
            <Text style={styles.statValue}>{highestOccupancy.displayHour}</Text>
            <Text style={[styles.statSubValue, { color: getOccupancyColor(highestOccupancy.percentage) }]}>
              {highestOccupancy.percentage}%
            </Text>
          </View>

          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Lowest</Text>
            <Text style={styles.statValue}>{lowestOccupancy.displayHour}</Text>
            <Text style={[styles.statSubValue, { color: getOccupancyColor(lowestOccupancy.percentage) }]}>
              {lowestOccupancy.percentage}%
            </Text>
          </View>

          <View style={styles.statBox}>
            <Text style={styles.statLabel}>Average</Text>
            <Text style={styles.statValue}>{avgOccupancy}%</Text>
          </View>
        </View>
      </View>
    </View>

  );
};

const styles = StyleSheet.create({
  title: {
    fontSize: 24,
    fontWeight: 600,
    paddingBottom: 10,
    paddingTop: 10,
  },
  container: {
    padding: 10,
    backgroundColor: 'white',
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    marginBottom: 20,
  },
  chartContainer: {
    maxHeight: 300,
  },
  barRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 4,
  },
  timeLabel: {
    width: 60,
    fontSize: 12,
    color: '#333',
  },
  barContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
  },
  bar: {
    height: 16,
    borderRadius: 2,
  },
  percentageLabel: {
    marginLeft: 8,
    fontSize: 12,
    color: '#666',
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 15,
    borderTopWidth: 1,
    borderTopColor: '#eee',
    paddingTop: 10,
  },
  statBox: {
    flex: 1,
    backgroundColor: '#f8f9fa',
    padding: 8,
    borderRadius: 6,
    alignItems: 'center',
    marginHorizontal: 4,
  },
  statLabel: {
    fontSize: 10,
    color: '#666',
    marginBottom: 2,
  },
  statValue: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  statSubValue: {
    fontSize: 12,
    fontWeight: 'bold',
  },
});