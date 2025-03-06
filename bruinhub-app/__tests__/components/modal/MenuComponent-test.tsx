import React from 'react';
import { render } from '@testing-library/react-native';
import MenuComponent from '@/components/modal/MenuComponent';
import { Colors } from '@/constants/Colors';

describe('MenuComponent', () => {
  // Sample menu data for testing
  const mockMenuSections = {
    'Appetizers': [
      'Garlic Bread',
      'Caesar Salad',
      'Chicken Wings'
    ],
    'Main Courses': [
      'Grilled Salmon',
      'Vegetarian Pasta',
      'Beef Steak'
    ],
    'Desserts': [
      'Chocolate Cake',
      'Ice Cream Sundae'
    ]
  };

  describe('Rendering', () => {
    it('renders "Menu" header', () => {
      const { getByText } = render(<MenuComponent sections={mockMenuSections} />);
      
      const menuHeader = getByText('Menu');
      expect(menuHeader).toBeTruthy();
    });

    it('renders all section titles', () => {
      const { getByText } = render(<MenuComponent sections={mockMenuSections} />);
      
      expect(getByText('Appetizers')).toBeTruthy();
      expect(getByText('Main Courses')).toBeTruthy();
      expect(getByText('Desserts')).toBeTruthy();
    });

    it('renders all menu items', () => {
      const { getByText } = render(<MenuComponent sections={mockMenuSections} />);
      
      // Appetizers
      expect(getByText('Garlic Bread')).toBeTruthy();
      expect(getByText('Caesar Salad')).toBeTruthy();
      expect(getByText('Chicken Wings')).toBeTruthy();

      // Main Courses
      expect(getByText('Grilled Salmon')).toBeTruthy();
      expect(getByText('Vegetarian Pasta')).toBeTruthy();
      expect(getByText('Beef Steak')).toBeTruthy();

      // Desserts
      expect(getByText('Chocolate Cake')).toBeTruthy();
      expect(getByText('Ice Cream Sundae')).toBeTruthy();
    });
  });

  describe('Conditional Rendering', () => {
    it('handles empty sections object', () => {
      const { queryByText } = render(<MenuComponent sections={{}} />);
      
      expect(queryByText('Menu')).toBeTruthy();
      expect(queryByText('Appetizers')).toBeNull();
    });

    it('handles section with no items', () => {
      const emptySectionMenu = {
        'Empty Section': []
      };

      const { getByText } = render(<MenuComponent sections={emptySectionMenu} />);
      
      expect(getByText('Empty Section')).toBeTruthy();
    });
  });

  describe('Unique Rendering Scenarios', () => {
    it('handles long menu sections', () => {
      const longMenuSections = {
        'Extremely Long Section Name': [
          'Very Long Dish Name 1',
          'Another Extremely Long Dish Description 2',
          'Yet Another Lengthy Menu Item 3'
        ]
      };

      const { getByText } = render(<MenuComponent sections={longMenuSections} />);
      
      expect(getByText('Extremely Long Section Name')).toBeTruthy();
      expect(getByText('Very Long Dish Name 1')).toBeTruthy();
    });

    it('renders multiple sections with varying number of items', () => {
      const variableSections = {
        'Single Item Section': ['Only One Dish'],
        'Multiple Items Section': [
          'Dish 1',
          'Dish 2',
          'Dish 3'
        ],
        'Empty Section': []
      };

      const { getByText, queryByText } = render(<MenuComponent sections={variableSections} />);
      
      expect(getByText('Single Item Section')).toBeTruthy();
      expect(getByText('Only One Dish')).toBeTruthy();
      
      expect(getByText('Multiple Items Section')).toBeTruthy();
      expect(getByText('Dish 1')).toBeTruthy();
      expect(getByText('Dish 2')).toBeTruthy();
      expect(getByText('Dish 3')).toBeTruthy();
      
      expect(getByText('Empty Section')).toBeTruthy();
    });
  });

  describe('Snapshot Testing', () => {
    it('matches snapshot', () => {
      const { toJSON } = render(<MenuComponent sections={mockMenuSections} />);
      
      expect(toJSON()).toMatchSnapshot();
    });
  });
});