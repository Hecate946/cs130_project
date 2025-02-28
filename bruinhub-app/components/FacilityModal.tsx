import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView } from "react-native";
import { ActivityIndicator, Button } from "react-native-paper";
import Modal from "react-native-modal";
import { CategoriesMap } from "@/constants/CategoriesMap";
import { SlugMap } from "@/constants/SlugMap";

interface FacilityModalProps {
  visible: boolean;
  onClose: () => void;
  facility: string | null;
}

// TODO change lol
const URL = "http://192.168.1.38:5001/api/v1/"

function getCategoryFromFacility(facilityName: string): string | undefined {
  for (const [category, facilityMap] of CategoriesMap.entries()) {
    for (const facility of facilityMap.values()) {
      if (facility === facilityName) {
        return category;
      }
    }
  }
  return undefined;
}

export default function FacilityModal({ visible, onClose, facility }: FacilityModalProps) {
  if (!facility) return null;

  const [facilityData, setFacilityData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchFacilityData = async () => {
    setLoading(true);
    try {
      const specificURL = URL + getCategoryFromFacility(facility) + "/" + SlugMap.get(facility);
      console.log(specificURL)
      const response = await fetch(specificURL);
      const data = await response.json();
      setFacilityData(data);
    } catch (error) {
      console.error("Error fetching facility data:", error);
    }
    setLoading(false);
  };

  useEffect(() => {
    if (visible) {
      fetchFacilityData();
    }
  }, [visible]);

  return (
    <Modal
      isVisible={visible}
      swipeDirection={["down"]}
      onSwipeComplete={onClose}
      onBackdropPress={onClose}
      useNativeDriver={true}
      propagateSwipe={true}
      avoidKeyboard={true}
      animationIn="slideInUp"
      animationOut="slideOutDown"
      swipeThreshold={70}
      backdropOpacity={0.5}
      style={styles.modal}
    >
      <View style={styles.modalContent}>
        <View style={styles.dragIndicator} />
        {loading && (
          <View style={styles.loadingBanner}>
            <ActivityIndicator size="small" color="#2774AE" />
          </View>
        )}

        {!loading && facilityData && (
          <ScrollView
            contentContainerStyle={styles.scrollViewContent}
            showsVerticalScrollIndicator={false}
            nestedScrollEnabled={true}
            bounces={true}
          >
            <Text style={styles.title}>{facility}</Text>
            <Text style={styles.description}>{facilityData?.data?.capacity || "No capacity details available."}</Text>
            <Text style={styles.description}>{JSON.stringify(facilityData?.data?.hours_today) || "No hours details available."}</Text>
            <Text style={styles.description}>{JSON.stringify(facilityData?.data?.menu) || "No menu details available."}</Text>
            <Text style={styles.description}>{JSON.stringify(facilityData?.data?.zones) || "No zone details available."}</Text>
            <Text style={styles.description}>{facilityData?.data?.last_updated || "No zone details available."}</Text>
            <Button onPress={onClose} mode="contained" style={styles.button}>
              Close
            </Button>
          </ScrollView>
        )}
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  modal: {
    justifyContent: "flex-end",
    margin: 0,
  },
  loadingBanner: {
    width: "100%",
    padding: 20,
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
  },
  dragIndicator: {
    width: 40,
    height: 5,
    backgroundColor: "#CCCCCC",
    borderRadius: 3,
    marginBottom: 15,
    alignSelf: "center",
  },
  scrollViewContent: {
    flexGrow: 1,
    paddingBottom: 30,
    width: "100%",
  },
  modalContent: {
    height: "85%",
    backgroundColor: "white",
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 25,
    alignItems: "center",
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
  },
  description: {
    marginVertical: 15,
    textAlign: "left",
    fontSize: 16,
  },
  button: {
    marginTop: 20,
  },
});
