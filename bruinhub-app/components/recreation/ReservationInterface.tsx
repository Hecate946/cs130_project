// components/recreation/ReservationInterface.tsx
import React, { useState, useEffect } from 'react';
import { View, Text, Button, ActivityIndicator, FlatList, StyleSheet, Alert } from 'react-native';
import { Calendar } from 'react-native-calendars';
import RNPickerSelect from 'react-native-picker-select';

interface Timeslot {
  id: string;
  time: string;
  available: boolean;
}

const facilities = [
  { label: 'Tennis', value: 'tennis' },
  { label: 'Pickleball', value: 'pickleball' }
];

const ReservationInterface: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [selectedFacility, setSelectedFacility] = useState<string | null>(null);
  const [timeslots, setTimeslots] = useState<Timeslot[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  // Function to fetch available timeslots for the given date and facility.
  const fetchTimeslots = async (date: string, facility: string) => {
    setLoading(true);
    try {
      // Replace with your backend endpoint and adjust query parameters as needed.
      const response = await fetch(`https://your-backend-url/api/timeslots?date=${date}&facility=${facility}`);
      if (!response.ok) {
        throw new Error('Failed to fetch timeslots');
      }
      const data: Timeslot[] = await response.json();
      setTimeslots(data);
    } catch (error) {
      console.error('Error fetching timeslots:', error);
      Alert.alert('Error', 'Could not fetch available timeslots. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Whenever both date and facility are selected, fetch available timeslots.
  useEffect(() => {
    if (selectedDate && selectedFacility) {
      fetchTimeslots(selectedDate, selectedFacility);
    }
  }, [selectedDate, selectedFacility]);

  // Function to reserve a selected timeslot.
  const handleReserve = async (timeslotId: string) => {
    try {
      // Replace with your backend reservation endpoint.
      const response = await fetch(`https://your-backend-url/api/reserve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          date: selectedDate,
          facility: selectedFacility,
          timeslotId: timeslotId
        })
      });
      if (!response.ok) {
        throw new Error('Reservation failed');
      }
      Alert.alert('Success', 'Your reservation is confirmed!');
      // Optionally update UI to mark the timeslot as reserved.
      setTimeslots(prev => prev.map(ts => ts.id === timeslotId ? { ...ts, available: false } : ts));
    } catch (error) {
      console.error('Reservation error:', error);
      Alert.alert('Error', 'Reservation failed. Please try again.');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Select a Date</Text>
    <Calendar
      onDayPress={(day: { dateString: string }) => setSelectedDate(day.dateString)}
      markedDates={selectedDate ? { [selectedDate]: { selected: true, selectedColor: 'blue' } } : {}}
    />

      <Text style={styles.title}>Select a Facility</Text>
    <RNPickerSelect
      onValueChange={(value: string | null) => setSelectedFacility(value)}
      items={facilities}
      placeholder={{ label: 'Select a facility...', value: null }}
      style={{
        inputIOS: styles.input,
        inputAndroid: styles.input,
      }}
    />

    {loading ? (
      <ActivityIndicator size="large" color="#0000ff" />
    ) : (
        <>
          <Text style={styles.title}>Available Timeslots</Text>
          {timeslots.length === 0 && selectedDate && selectedFacility ? (
            <Text>No available timeslots for the selected date and facility.</Text>
          ) : (
            <FlatList
              data={timeslots}
              keyExtractor={(item) => item.id}
              renderItem={({ item }) => (
                <View style={styles.timeslotItem}>
                  <Text>{item.time}</Text>
                  <Button
                    title="Reserve"
                    onPress={() => handleReserve(item.id)}
                    disabled={!item.available}
                  />
                </View>
              )}
            />
          )}
        </>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  title: { fontSize: 18, marginVertical: 8 },
  input: {
    padding: 12,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 4,
    marginVertical: 8
  },
  timeslotItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee'
  }
});

export default ReservationInterface;
