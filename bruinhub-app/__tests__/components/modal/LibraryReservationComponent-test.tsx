import React from 'react';
import { render } from '@testing-library/react-native';
import LibraryReservationComponent from '@/components/modal/LibraryReservationComponent';

describe('LibraryReservationComponent', () => {
  // Mock data for testing
  const mockRoomsData = [
    {
      id: 1,
      room_id: 1,
      start_time: '2024-03-04T10:00:00',
      end_time: '2024-03-04T11:30:00',
      status: 'available'
    },
    {
      id: 2,
      room_id: 1,
      start_time: '2024-03-04T13:00:00',
      end_time: '2024-03-04T14:30:00',
      status: 'available'
    },
    {
      id: 3,
      room_id: 2,
      start_time: '2024-03-04T15:00:00',
      end_time: '2024-03-04T16:30:00',
      status: 'available'
    },
    {
      id: 4,
      room_id: 3,
      start_time: '2024-03-04T10:00:00',
      end_time: '2024-03-04T11:30:00',
      status: 'booked'
    }
  ];

  describe('Rendering', () => {
    it('renders "Today\'s Reservations" header when rooms are available', () => {
      const availableRooms = mockRoomsData.filter(room => room.status === 'available');
      const { getByText } = render(<LibraryReservationComponent roomsData={availableRooms} />);
      
      expect(getByText("Today's Reservations")).toBeTruthy();
    });

    it('renders correct number of rooms', () => {
      const availableRooms = mockRoomsData.filter(room => room.status === 'available');
      const { getAllByText } = render(<LibraryReservationComponent roomsData={availableRooms} />);
      
      const roomTitles = getAllByText(/Room \d+/);
      expect(roomTitles).toHaveLength(2); // Room 1 and Room 2
    });

    it('renders time slots for each room', () => {
      const availableRooms = mockRoomsData.filter(room => room.status === 'available');
      const { getByText } = render(<LibraryReservationComponent roomsData={availableRooms} />);
      
      // Check time slots for Room 1
      expect(getByText(/10:00 AM - 11:30 AM/)).toBeTruthy();
      expect(getByText(/01:00 PM - 02:30 PM/)).toBeTruthy();
      
      // Check time slot for Room 2
      expect(getByText(/03:00 PM - 04:30 PM/)).toBeTruthy();
    });
  });

  describe('Conditional Rendering', () => {
    it('displays "No reservations" message when no available rooms', () => {
      const noAvailableRooms = mockRoomsData.filter(room => room.status === 'booked');
      const { getByText } = render(<LibraryReservationComponent roomsData={noAvailableRooms} />);
      
      expect(getByText("No reservations for the rest of the day.")).toBeTruthy();
    });

    it('filters out non-available rooms', () => {
      const { queryByText } = render(<LibraryReservationComponent roomsData={mockRoomsData} />);
      
      // Room 3 (booked) should not be rendered
      expect(queryByText('Room 3')).toBeNull();
    });
  });

  describe('Time Formatting', () => {
    it('formats time correctly', () => {
      const availableRooms = mockRoomsData.filter(room => room.status === 'available');
      const { getByText } = render(<LibraryReservationComponent roomsData={availableRooms} />);
      
      // Check if times are in the correct format (HH:MM AM/PM)
      const timeSlots = [
        '10:00 AM - 11:30 AM',
        '01:00 PM - 02:30 PM',
        '03:00 PM - 04:30 PM'
      ];

      timeSlots.forEach(timeSlot => {
        expect(getByText(timeSlot)).toBeTruthy();
      });
    });
  });

  describe('Styling', () => {
    it('applies correct style to "No reservations" message', () => {
      const noAvailableRooms = mockRoomsData.filter(room => room.status === 'booked');
      const { getByText } = render(<LibraryReservationComponent roomsData={noAvailableRooms} />);
      
      const noReservationsText = getByText("No reservations for the rest of the day.");
      
      expect(noReservationsText.props.style).toEqual(expect.objectContaining({
        marginVertical: 15,
        textAlign: "left",
        fontSize: 16,
        width: "100%"
      }));
    });
  });

  describe('Edge Cases', () => {
    it('handles empty rooms data array', () => {
      const { getByText } = render(<LibraryReservationComponent roomsData={[]} />);
      
      expect(getByText("No reservations for the rest of the day.")).toBeTruthy();
    });

    it('handles multiple time slots in the same room', () => {
      const availableRooms = mockRoomsData.filter(room => room.status === 'available');
      const { getByText } = render(<LibraryReservationComponent roomsData={availableRooms} />);
      
      const roomOneTimes = [
        '10:00 AM - 11:30 AM',
        '01:00 PM - 02:30 PM'
      ];

      roomOneTimes.forEach(time => {
        expect(getByText(time)).toBeTruthy();
      });
    });
  });

  describe('Snapshot Testing', () => {
    it('matches snapshot for available rooms', () => {
      const availableRooms = mockRoomsData.filter(room => room.status === 'available');
      const { toJSON } = render(<LibraryReservationComponent roomsData={availableRooms} />);
      
      expect(toJSON()).toMatchSnapshot();
    });

    it('matches snapshot for no available rooms', () => {
      const noAvailableRooms = mockRoomsData.filter(room => room.status === 'booked');
      const { toJSON } = render(<LibraryReservationComponent roomsData={noAvailableRooms} />);
      
      expect(toJSON()).toMatchSnapshot();
    });
  });
});