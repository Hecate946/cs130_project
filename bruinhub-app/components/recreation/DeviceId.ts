import DeviceInfo from 'react-native-device-info';

/**
 * Fetches the unique device ID.
 * @returns {Promise<string>} The unique device identifier.
 */
export const getDeviceId = async (): Promise<string> => {
  try {
    const deviceId = await DeviceInfo.getUniqueId();
    console.log('Device ID:', deviceId);
    return deviceId;
  } catch (error) {
    console.error('Error fetching device ID:', error);
    return 'unknown-device';
  }
};
