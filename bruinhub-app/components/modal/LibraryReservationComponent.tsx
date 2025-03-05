import React from "react";
import { View, Text, FlatList, StyleSheet } from "react-native";

interface RoomSlot {
	id: number;
	room_id: number;
	start_time: string;
	end_time: string;
	status: string;
};

interface LibraryReservationComponentProps {
	roomsData: RoomSlot[];
};

export default function LibraryReservationComponent({ roomsData }: LibraryReservationComponentProps) {
	const availableRooms = roomsData
		.filter((slot) => slot.status === "available")
		.reduce<{ [key: number]: RoomSlot[] }>((acc, slot) => {
			if (!acc[slot.room_id]) {
				acc[slot.room_id] = [];
			}
			acc[slot.room_id].push(slot);
			return acc;
		}, {});

	return (
		<View>
			{
				Object.keys(availableRooms).length > 0 ?
					<View>
						<Text style={styles.text}>Today's Reservations</Text>
						<FlatList
							data={Object.entries(availableRooms)}
							keyExtractor={([roomId]) => roomId}
							scrollEnabled={false}
							renderItem={({ item: [roomId, slots] }) => (
								<View style={styles.roomContainer}>
									<Text style={styles.roomTitle}>Room {roomId}</Text>
									{slots.map((slot) => (
										<View key={slot.id} style={styles.slot}>
											<Text style={styles.time}>
												{new Date(slot.start_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} -{` `}
												{new Date(slot.end_time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
											</Text>
										</View>
									))}
								</View>
							)}
						/>
					</View> :
					<Text style={styles.description}>No reservations for the rest of the day.</Text>
			}
		</View>
	);
};

const styles = StyleSheet.create({
	roomContainer: {
		padding: 10,
		marginBottom: 10,
		backgroundColor: "#fff",
		borderRadius: 8,
		shadowColor: "#000",
		shadowOpacity: 0.1,
		shadowOffset: { width: 0, height: 2 },
		shadowRadius: 4,
		elevation: 2,
	},
	roomTitle: {
		fontSize: 18,
		fontWeight: "bold",
		marginBottom: 5,
	},
	slot: {
		paddingVertical: 5,
	},
	time: {
		fontSize: 16,
		color: "#333",
	},
	text: {
		fontSize: 22,
		fontWeight: 600,
		paddingBottom: 10,
	},
	description: {
    marginVertical: 15,
    textAlign: "left",
    fontSize: 16,
    width: "100%",
  },
});
