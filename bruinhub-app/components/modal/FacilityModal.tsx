import React, { useEffect, useState, useRef, useCallback } from "react";
import { View, Text, StyleSheet, ScrollView, Platform, Dimensions, PanResponder, Animated } from "react-native";
import { ActivityIndicator, Button } from "react-native-paper";
import Modal from "react-native-modal";
import { Categories } from "@/constants/Categories";
import { CategoriesMap } from "@/constants/CategoriesMap";
import { SlugMap } from "@/constants/SlugMap";
import { Colors } from "@/constants/Colors";
import MenuComponent from "./MenuComponent";
import CapacityComponent from "./CapacityComponent";
import DateFormatter from "./DateFormatter";
import OperatingHoursComponent from "./OperatingHoursComponent";
import GymOperatingHoursComponent from "./GymOperatingHoursComponent";
import GymZonesComponent from "./GymZonesComponent";
import LibraryReservationComponent from "./LibraryReservationComponent";
import FeastMenuComponent from "./FeastMenuComponent";
import NotificationBell from "../NotificationBellComponent";
import HistoricalDataComponent from "./HistoricalDataComponent";

interface FacilityModalProps {
  visible: boolean;
  onClose: () => void;
  facility: string | null;
}

interface FacilityData {
  data: object,
}

// TODO change lol
const URL = "http://192.168.1.38:5001/api/v1/";

const { height: SCREEN_HEIGHT } = Dimensions.get("window");
const SWIPE_THRESHOLD = 100;
const DRAG_INDICATOR_ZONE_HEIGHT = 50;

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

function getFacilityId(facilityName: string): number | undefined {
  for (const [, facilityMap] of CategoriesMap.entries()) {
    for (const [id, name] of facilityMap.entries()) {
      if (name === facilityName) {
        return parseInt(id, 10);
      }
    }
  }
  return undefined;
}

export default function FacilityModal({ visible, onClose, facility }: FacilityModalProps) {
  const [facilityData, setFacilityData] = useState<FacilityData>(null);
  const [historicalData, setHistoricalData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isModalReady, setIsModalReady] = useState(false);
  const [isClosing, setIsClosing] = useState(false);

  const translateY = useRef(new Animated.Value(0)).current;
  const isDraggingHeader = useRef(false);
  const scrollViewRef = useRef(null);

  useEffect(() => {
    if (visible) {
      setIsClosing(false);
      setTimeout(() => setIsModalReady(true), 100);
      translateY.setValue(0);
    } else {
      setTimeout(() => setIsModalReady(false), 100);
    }
  }, [visible]);

  const animatedCloseModal = useCallback(() => {
    setIsClosing(true);
    setFacilityData(null);
    setHistoricalData(null);
    Animated.timing(translateY, {
      toValue: SCREEN_HEIGHT,
      duration: 200,
      useNativeDriver: true,
    }).start(() => {
      onClose();
    });
  }, [translateY, onClose]);

  const handleClosePress = useCallback(() => {
    animatedCloseModal();
  }, [animatedCloseModal]);

  const handleBackdropPress = useCallback(() => {
    animatedCloseModal();
  }, [animatedCloseModal]);

  const dragIndicatorPanResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => true,
      onMoveShouldSetPanResponder: () => true,
      onPanResponderGrant: () => {
        isDraggingHeader.current = true;
        translateY.setOffset(0);
        translateY.setValue(0);
      },
      onPanResponderMove: (_, gestureState) => {
        if (gestureState.dy > 0) {
          translateY.setValue(gestureState.dy);
        }
      },
      onPanResponderRelease: (_, gestureState) => {
        isDraggingHeader.current = false;

        if (gestureState.dy > SWIPE_THRESHOLD) {
          animatedCloseModal();
        } else {
          Animated.spring(translateY, {
            toValue: 0,
            friction: 8,
            tension: 40,
            useNativeDriver: true,
          }).start();
        }
      },
      onPanResponderTerminate: () => {
        isDraggingHeader.current = false;
        Animated.spring(translateY, {
          toValue: 0,
          friction: 8,
          tension: 40,
          useNativeDriver: true,
        }).start();
      },
    })
  ).current;

  const fetchFacilityData = useCallback(async () => {
    if (!facility) return;

    setLoading(true);
    try {
      const category = getCategoryFromFacility(facility);
      const slug = SlugMap.get(facility);

      if (!category || !slug) {
        console.error("Invalid facility data", { facility, category, slug });
        setLoading(false);
        return;
      }

      let specificURL = "";
      let response;
      const now = new Date();
      const start = now.getFullYear() + '-' +
        String(now.getMonth() + 1).padStart(2, '0') + '-' +
        String(now.getDate()).padStart(2, '0') + 'T' +
        String(now.getHours()).padStart(2, '0') + ':' +
        String(now.getMinutes()).padStart(2, '0') + ':' +
        String(now.getSeconds()).padStart(2, '0');

      const endOfDay = new Date();
      endOfDay.setHours(23, 59, 59, 0); // Set to the end of the current day (local time)
      const end = endOfDay.getFullYear() + '-' +
        String(endOfDay.getMonth() + 1).padStart(2, '0') + '-' +
        String(endOfDay.getDate()).padStart(2, '0') + 'T' +
        String(endOfDay.getHours()).padStart(2, '0') + ':' +
        String(endOfDay.getMinutes()).padStart(2, '0') + ':' +
        String(endOfDay.getSeconds()).padStart(2, '0');

      if (category === "library") {
        specificURL = `${URL}${category}/${slug}/bookings/range?start=${start}&end=${end}`;
      } else {
        specificURL = `${URL}${category}/${slug}`;
      }

      console.log(specificURL); // TODO remove

      response = await fetch(specificURL);
      const responseText = await response.text();
      const data = JSON.parse(responseText);
      setFacilityData(data);

      // Get historical data if possible
      if (category === 'dining' || category === 'gym') {
        const historicalURL = `${URL}/historical/${category}/${slug}`;
        const historicalRes = await fetch(historicalURL);
        const historicalResText = await historicalRes.text();
        const historical = JSON.parse(historicalResText);
        setHistoricalData(historical);
      }
    } catch (error) {
      console.error("Error fetching facility data:", error);
      console.error("Full error details:", {
        message: error.message,
        stack: error.stack,
        response: error.response
      });
    } finally {
      setLoading(false);
    }
  }, [facility]);

  useEffect(() => {
    if (visible && facility && isModalReady) {
      fetchFacilityData();
    }
  }, [visible, facility, isModalReady, fetchFacilityData]);

  if (!visible || !facility) {
    return null;
  }

  return (
    <Modal
      isVisible={visible && isModalReady}
      onBackdropPress={handleBackdropPress}
      useNativeDriver
      animationIn="slideInUp"
      animationOut="slideOutDown"
      animationInTiming={300}
      animationOutTiming={300}
      backdropTransitionInTiming={300}
      backdropTransitionOutTiming={300}
      style={styles.modal}
      backdropOpacity={0.5}
      statusBarTranslucent
      hideModalContentWhileAnimating
      swipeDirection={undefined}
      propagateSwipe={false}
    >
      <Animated.View
        style={[
          styles.modalContent,
          { transform: [{ translateY }] }
        ]}
      >
        <View
          style={styles.dragIndicatorZone}
          {...dragIndicatorPanResponder.panHandlers}
        >
          <View style={styles.dragIndicator} />
        </View>

        {loading ? (
          <View style={styles.loadingBanner} testID="loading-indicator">
            <ActivityIndicator size="small" color="#2774AE" />
          </View>
        ) : facilityData ? (
          <ScrollView
            ref={scrollViewRef}
            contentContainerStyle={styles.scrollViewContent}
            showsVerticalScrollIndicator={false}
            nestedScrollEnabled
            bounces
            scrollEnabled={!isDraggingHeader.current}
            keyboardShouldPersistTaps="handled"
            testID="drag-indicator"
          >
            <View style={styles.titleContainer}>
              <Text style={styles.title}>{facility}</Text>
              <NotificationBell facilityId={getFacilityId(facility)} />
            </View>

            {/* Hours Display */}
            {
              getCategoryFromFacility(facility) === 'dining' &&
              <OperatingHoursComponent hoursToday={facilityData?.data?.hours_today} />
            }
            {
              getCategoryFromFacility(facility) === 'gym' &&
              <GymOperatingHoursComponent
                regularHours={facilityData?.data?.regular_hours}
                specialHours={facilityData?.data?.special_hours}
              />
            }

            {/* Occupancy Data */}
            {
              facilityData?.data?.occupants != null && facilityData?.data?.capacity > 0 && (
                <CapacityComponent
                  percentage={facilityData.data.occupants / facilityData.data.capacity}
                />
              )
            }
            {
              getCategoryFromFacility(facility) === 'gym' &&
              <GymZonesComponent zones={facilityData?.data?.zones} />
            }

            {/* Menu Display */}
            {
              (facilityData?.data?.menu &&
                Object.keys(facilityData.data.menu).length > 0) ?
                facility === "Feast" ?
                  <FeastMenuComponent menuData={facilityData.data.menu} /> :
                  <MenuComponent sections={facilityData?.data?.menu} /> :
                null
            }

            {/* Historical Occupancy Data */}
            {
              historicalData && getCategoryFromFacility(facility) === 'dining' &&
              <HistoricalDataComponent data={historicalData?.data} />
            }

            {/* Library Reservation Display, only shows the reservations for the rest of the day */}
            {
              (getCategoryFromFacility(facility) === 'library' && facilityData.data) ?
                <LibraryReservationComponent roomsData={facilityData?.data} /> :
                getCategoryFromFacility(facility) === 'library' &&
                <Text style={styles.libraryDescription}>No availabilities for the rest of the day</Text>

            }
            {
              getCategoryFromFacility(facility) !== 'library' &&
              (<View style={styles.dateView}>
                <Text style={styles.dateText}>Last updated:</Text>
                <DateFormatter isoString={facilityData?.data?.last_updated} />
              </View>)
            }

            <View style={styles.buttonView}>
              <Button
                onPress={handleClosePress}
                mode="contained"
                style={styles.button}
                contentStyle={styles.buttonContent}
                labelStyle={styles.buttonLabel}
              >
                Close
              </Button>
            </View>
          </ScrollView>
        ) : null}
      </Animated.View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  modal: {
    justifyContent: "flex-end",
    margin: 0,
  },
  dragIndicatorZone: {
    width: '100%',
    height: DRAG_INDICATOR_ZONE_HEIGHT,
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: 25,
    paddingBottom: 20,
  },
  dragIndicator: {
    width: 40,
    height: 5,
    backgroundColor: Colors.light.shade,
    borderRadius: 3,
  },
  loadingBanner: {
    width: "100%",
    padding: 20,
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
  },
  scrollViewContent: {
    flexGrow: 1,
    paddingBottom: 30,
    width: "100%",
  },
  modalContent: {
    height: "85%",
    backgroundColor: Colors.light.background,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 25,
    paddingTop: 0,
    width: "100%",
    overflow: 'hidden',
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: -3 },
        shadowOpacity: 0.1,
        shadowRadius: 3,
      },
      android: {
        elevation: 5,
      },
    }),
  },
  titleContainer: {
    flexDirection: "row",
    alignItems: "center",
    width: "100%",
    flex: 0,
    justifyContent: "space-between",
  },
  title: {
    fontSize: 32,
    fontWeight: "bold",
    paddingTop: 10,
    paddingBottom: 10,
  },
  description: {
    marginVertical: 15,
    textAlign: "left",
    fontSize: 16,
    width: "100%",
  },
  dateText: {
    textAlign: "left",
    fontSize: 16,
    fontStyle: "italic",
  },
  dateView: {
    flexDirection: "row",
    alignItems: "center",
  },
  buttonView: {
    alignItems: "center",
  },
  button: {
    marginTop: 30,
    width: "60%",
    backgroundColor: Colors.light.shade,
    borderRadius: 60,
  },
  buttonLabel: {
    fontSize: 18,
    color: Colors.light.background,
    textTransform: "uppercase",
    width: "100%",
  },
  buttonContent: {
    justifyContent: "center",
    alignItems: "center",
    height: 50,
  },
  libraryDescription: {
    marginVertical: 15,
    textAlign: "center",
    fontSize: 16,
    width: "100%",
    paddingTop: 20,
    paddingBottom: 10,
    fontStyle: "italic",
  }
});
