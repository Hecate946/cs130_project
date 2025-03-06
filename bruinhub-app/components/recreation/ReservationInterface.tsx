import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ActivityIndicator,
  FlatList,
  StyleSheet,
  Alert,
  TouchableOpacity,
  Platform,
} from 'react-native';
import { Calendar } from 'react-native-calendars';
import RNPickerSelect from 'react-native-picker-select';
import LogoutButton from './LogoutButton';
import { getDeviceId } from './DeviceId';

const BACKEND_HOST =
  Platform.OS === 'android' ? 'http://10.0.2.2:5001/api' : 'http://localhost:5001/api';

// Hardcoded facilities list
const facilities = [
  { label: 'Sunset Pickleball', value: '02a10035-6fd3-48b1-9a1f-648f6368c09a' },
  { label: 'Sunset Tennis', value: '1925f835-e7cd-422b-bf9e-124dadf1a6aa' },
  { label: 'Sycamore Tennis', value: '73dc0950-4702-467d-ac49-792e7b2beab6' },
];

interface Timeslot {
  id: string;
  time: string;
  aid: string;
  tsId: string;
  tsiId: string;
  spots: number;           // Number of available sub-slots
  availability: string;    // "available", "unavailable", or "booked"
}

interface Court {
  courtId: string;
  courtName: string;
  availableSlots: number;  // Total available timeslots for this court
  slots: Timeslot[];
}

const ReservationInterface: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [selectedFacility, setSelectedFacility] = useState<string | null>(null);
  const [courts, setCourts] = useState<Court[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  // Fetch available courts and timeslots from the backend.
  const fetchAvailableCourts = async (dateString: string, facilityId: string) => {
    setLoading(true);
    try {
      const deviceId = await getDeviceId();
      const [year, month, day] = dateString.split('-');
      const endpoint = `${BACKEND_HOST}/v1/rec/available-courts?deviceId=${deviceId}&facilityId=${facilityId}&year=${year}&month=${month}&day=${day}`;
      console.log('Fetching endpoint:', endpoint);
      const response = await fetch(endpoint, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response.ok) {
        throw new Error(`Failed to fetch available courts: ${response.status}`);
      }
      const data = await response.json();
      console.log('Backend returned:', data);
      setCourts(data.availableCourts || []);
    } catch (error) {
      console.error('Error fetching available courts:', error);
      Alert.alert('Error', 'Could not fetch available timeslots. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Re-fetch available courts whenever either date or facility changes.
  useEffect(() => {
    if (selectedDate && selectedFacility) {
      // Clear courts so that the loading indicator shows until new data arrives
      setCourts([]);
      fetchAvailableCourts(selectedDate, selectedFacility);
    }
  }, [selectedDate, selectedFacility]);

  // Handler to reserve a specific timeslot.
  const handleReserve = async (courtId: string, timeslot: Timeslot) => {
    if (timeslot.availability !== 'available' || timeslot.spots === 0) return;
    try {
      const deviceId = await getDeviceId();
      const payload = {
        device_id: deviceId,
        facilityId: selectedFacility,
        courtId: courtId,
        date: selectedDate, // format "YYYY-MM-DD"
        timeslot: {
          time: timeslot.time,
          aid: timeslot.aid,
          tsId: timeslot.tsId,
          tsiId: timeslot.tsiId,
        },
      };
      console.log('Reservation payload:', payload);
      const response = await fetch(`${BACKEND_HOST}/v1/rec/reserve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error('Reservation failed');
      Alert.alert('Success', 'Your reservation is confirmed!');
      // Update local state to mark the reserved timeslot as booked.
      setCourts(prev =>
        prev.map(court => {
          if (court.courtId === courtId) {
            return {
              ...court,
              slots: court.slots.map(slot =>
                slot.id === timeslot.id ? { ...slot, availability: 'booked', spots: 0 } : slot
              ),
              availableSlots: Math.max(court.availableSlots - 1, 0),
            };
          }
          return court;
        })
      );
    } catch (error) {
      console.error('Reservation error:', error);
      Alert.alert('Error', 'Reservation failed. Please try again.');
    }
  };

  // Render each timeslot row with unique key and conditional styling.
  const renderTimeslot = (courtId: string, timeslot: Timeslot, index: number) => {
    const { time, spots, availability } = timeslot;
    let buttonLabel = 'BOOK NOW';
    let buttonDisabled = false;
    let buttonStyle = styles.buttonAvailable;
    if (availability === 'booked') {
      buttonLabel = 'BOOKED';
      buttonDisabled = true;
      buttonStyle = styles.buttonBooked;
    } else if (availability === 'unavailable' || spots === 0) {
      buttonLabel = 'UNAVAILABLE';
      buttonDisabled = true;
      buttonStyle = styles.buttonUnavailable;
    }
    return (
      <View
        key={timeslot.id ? timeslot.id : `${courtId}-slot-${index}`}
        style={styles.timeslotRow}
      >
        <View style={styles.timeslotInfo}>
          <Text style={styles.timeslotTime}>{time}</Text>
          {spots > 0 ? (
            <Text style={styles.spotsInfo}>{spots} spots available</Text>
          ) : (
            <Text style={styles.spotsInfo}>No spots available</Text>
          )}
        </View>
        <TouchableOpacity
          style={[styles.reserveButton, buttonStyle]}
          onPress={() => handleReserve(courtId, timeslot)}
          disabled={buttonDisabled}
        >
          <Text style={styles.buttonText}>{buttonLabel}</Text>
        </TouchableOpacity>
      </View>
    );
  };

  // ListHeader: Displays the logout button, facility selector, and date selector.
  const ListHeader = () => (
    <View>
      <View style={styles.logoutContainer}>
        <LogoutButton />
      </View>
      <Text style={styles.title}>Select a Facility</Text>
      <RNPickerSelect
        onValueChange={(value: string | null) => setSelectedFacility(value)}
        items={facilities}
        placeholder={{ label: 'Select a facility...', value: null }}
        value={selectedFacility}
        style={{
          inputIOS: styles.input,
          inputAndroid: styles.input,
        }}
      />
      <Text style={styles.title}>Select a Date</Text>
      <Calendar
        onDayPress={(day: { dateString: string }) => setSelectedDate(day.dateString)}
        markedDates={selectedDate ? { [selectedDate]: { selected: true, selectedColor: 'blue' } } : {}}
      />
      <Text style={styles.title}>Available Timeslots</Text>
      {(!selectedDate || !selectedFacility) && (
        <Text>Please select a facility and a date.</Text>
      )}
    </View>
  );

  return (
    <FlatList
      contentContainerStyle={styles.contentContainer}
      data={courts}
      keyExtractor={(court) => court.courtId}
      renderItem={({ item: court }) => (
        <View style={styles.courtContainer} key={court.courtId}>
          <Text style={styles.courtTitle}>{court.courtName}</Text>
          {court.slots.length === 0 ? (
            <Text>No timeslots available for this court.</Text>
          ) : (
            court.slots.map((slot, index) => renderTimeslot(court.courtId, slot, index))
          )}
        </View>
      )}
      ListHeaderComponent={ListHeader}
      ListEmptyComponent={
        loading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#0000ff" />
          </View>
        ) : selectedDate && selectedFacility ? (
          <Text>No available timeslots for the selected date and facility.</Text>
        ) : null
      }
      ListFooterComponent={<View style={{ height: 40 }} />}
    />
  );
};

const styles = StyleSheet.create({
  contentContainer: {
    padding: 16,
    paddingBottom: 40,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    marginVertical: 16,
  },
  logoutContainer: {
    marginBottom: 16,
    alignItems: 'flex-end',
  },
  title: {
    fontSize: 18,
    marginVertical: 8,
    fontWeight: 'bold',
  },
  input: {
    padding: 12,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 4,
    marginVertical: 8,
  },
  courtContainer: {
    marginVertical: 8,
    padding: 8,
    borderWidth: 1,
    borderColor: '#eee',
    borderRadius: 4,
  },
  courtTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  timeslotRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 6,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  timeslotInfo: {
    flex: 1,
  },
  timeslotTime: {
    fontSize: 15,
    marginBottom: 2,
  },
  spotsInfo: {
    color: '#777',
    fontSize: 14,
  },
  reserveButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4,
  },
  buttonAvailable: {
    backgroundColor: '#1abc9c',
  },
  buttonBooked: {
    backgroundColor: '#999',
  },
  buttonUnavailable: {
    backgroundColor: '#ccc',
  },
  buttonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
});

export default ReservationInterface;
