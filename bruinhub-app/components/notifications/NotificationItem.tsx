import { StyleSheet, Text, View } from "react-native";
import { Switch } from 'react-native-paper';
import Slider from '@react-native-community/slider';
import { Colors } from "@/constants/Colors";
import * as Haptics from "expo-haptics";
import { useState, useEffect } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { SlugMap } from "@/constants/SlugMap";

interface NotificationItemProps {
  name: string,
  id: string,
  onPreferenceChange?: (slug: string, enabled: boolean, threshold: number) => void;
};

interface NotificationPreference {
  enabled: boolean;
  threshold: number;
}

export default function NotificationItem({name, id, onPreferenceChange} : NotificationItemProps) {
  const [preferences, setPreferences] = useState<NotificationPreference>({
    enabled: false,
    threshold: 50
  });

  useEffect(() => {
    const loadPreferences = async () => {
      try {
        const storedValue = await AsyncStorage.getItem(`notification_${id}`);
        if (storedValue) {
          const parsedPrefs = JSON.parse(storedValue);
          setPreferences(parsedPrefs);
        } else {
          // If no stored preferences, set to disabled by default
          const defaultPrefs = {
            enabled: false,
            threshold: 50
          };
          await AsyncStorage.setItem(`notification_${id}`, JSON.stringify(defaultPrefs));
          setPreferences(defaultPrefs);
        }
      } catch (error) {
        console.error("Error loading preferences:", error);
        // Even on error, ensure we're in a disabled state
        setPreferences({
          enabled: false,
          threshold: 50
        });
      }
    };

    loadPreferences();
  }, [id, name]);

  const updatePreferences = async (newPrefs: Partial<NotificationPreference>) => {
    try {
      const updatedPrefs = { ...preferences, ...newPrefs };
      setPreferences(updatedPrefs);
      await AsyncStorage.setItem(`notification_${id}`, JSON.stringify(updatedPrefs));
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);

      // Get the slug for this facility
      const slug = SlugMap.get(name);
      if (slug && onPreferenceChange) {
        onPreferenceChange(slug, updatedPrefs.enabled, updatedPrefs.threshold);
      }
    } catch (error) {
      console.error("Error updating preferences:", error);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.row}>
        <Text style={styles.itemText}>
          {name}
        </Text>
        <Switch
          color={Colors.light.tint}
          value={preferences.enabled}
          onValueChange={(value) => updatePreferences({ enabled: value })}
        />
      </View>
      {preferences.enabled && (
        <View style={styles.sliderContainer}>
          <Text style={styles.thresholdText}>
            Notify when capacity exceeds {preferences.threshold}%
          </Text>
          <Slider
            value={preferences.threshold}
            onValueChange={(value: number) => updatePreferences({ threshold: value })}
            minimumValue={0}
            maximumValue={100}
            step={5}
            style={styles.slider}
            minimumTrackTintColor={Colors.light.tint}
            maximumTrackTintColor={Colors.light.shade}
            thumbTintColor={Colors.light.tint}
          />
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: "white",
    borderBottomWidth: 1,
    borderBottomColor: "#ddd",
    width: "100%",
    borderRadius: 10,
    padding: 16,
  },

  row: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },

  itemText: {
    fontSize: 16,
    fontWeight: "300",
  },

  sliderContainer: {
    marginTop: 8,
  },

  thresholdText: {
    fontSize: 14,
    color: Colors.light.text,
    marginBottom: 4,
  },

  slider: {
    height: 40,
  },
});
