import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import CapacityComponent from './CapacityComponent';
import { Colors } from '@/constants/Colors';

type Zone = {
  capacity: number;
  occupants: number;
  last_updated: string;
};

interface GymZonesComponentProps {
  zones: {
    [key: string]: Zone;
  };
}

export default function GymZonesComponent({ zones }: GymZonesComponentProps) {
  return (
    <View style={styles.container}>
      {Object.entries(zones).map(([zoneName, zoneData]) => (
        <View key={zoneName} style={styles.zoneContainer}>
          <Text style={styles.zoneName}>{zoneName}</Text>
          <CapacityComponent percentage={zoneData.occupants / zoneData.capacity} />
        </View>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 10,
  },
  zoneContainer: {
    marginBottom: 15,
    padding: 10,
    backgroundColor: Colors.light.background,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  zoneName: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  zoneInfo: {
    fontSize: 14,
    color: Colors.light.text,
    marginBottom: 10,
  },
});
