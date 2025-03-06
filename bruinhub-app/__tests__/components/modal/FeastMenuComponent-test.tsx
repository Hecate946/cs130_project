import React from 'react';
import { render } from '@testing-library/react-native';
import FeastMenuComponent from '@/components/modal/FeastMenuComponent';

describe('FeastMenuComponent', () => {
  // Sample menu data for testing
  const mockMenuData = {
    'Appetizers': {
      image: null,
      items: ['Salad', 'Bruschetta', 'Soup']
    },
    'Main Courses': {
      image: null,
      items: ['Steak', 'Salmon', 'Vegetarian Pasta']
    },
    'Desserts': {
      image: null,
      items: ['Chocolate Cake', 'Ice Cream']
    },
    'Empty Section': {
      image: null,
      items: []
    }
  };

  // Rendering tests
  describe('Rendering', () => {
    it('renders the main "Menu" title', () => {
      const { getByText } = render(<FeastMenuComponent menuData={mockMenuData} />);
      
      const menuTitle = getByText('Menu');
      expect(menuTitle).toBeTruthy();
    });

    it('renders all section titles', () => {
      const { getByText } = render(<FeastMenuComponent menuData={mockMenuData} />);
      
      expect(getByText('Appetizers')).toBeTruthy();
      expect(getByText('Main Courses')).toBeTruthy();
      expect(getByText('Desserts')).toBeTruthy();
    });

    it('renders menu items for each section', () => {
      const { getByText } = render(<FeastMenuComponent menuData={mockMenuData} />);
      
      // Check a few sample menu items
      expect(getByText('Salad')).toBeTruthy();
      expect(getByText('Steak')).toBeTruthy();
      expect(getByText('Chocolate Cake')).toBeTruthy();
    });

    it('does not render empty sections', () => {
      const { queryByText } = render(<FeastMenuComponent menuData={mockMenuData} />);
      
      // Empty section should not be rendered
      expect(queryByText('Empty Section')).toBeNull();
    });
  });

  // Styling tests
  describe('Styling', () => {
    it('applies correct style to main title', () => {
      const { getByText } = render(<FeastMenuComponent menuData={mockMenuData} />);
      const menuTitle = getByText('Menu');
      
      expect(menuTitle.props.style).toEqual(expect.objectContaining({
        fontSize: 24,
        textTransform: "uppercase",
        fontWeight: 600,
        paddingBottom: 5,
        paddingTop: 10,
      }));
    });

    it('matches snapshot for visual regression', () => {
      const { toJSON } = render(<FeastMenuComponent menuData={mockMenuData} />);
      
      expect(toJSON()).toMatchSnapshot();
    });
  });

  // Edge cases
  describe('Edge Cases', () => {
    it('handles empty menu data', () => {
      const { getByText, queryByText } = render(<FeastMenuComponent menuData={{}} />);
      
      // Menu title should still be present
      expect(getByText('Menu')).toBeTruthy();
      
      // No section titles should be rendered
      expect(queryByText('Appetizers')).toBeNull();
      expect(queryByText('Main Courses')).toBeNull();
    });

    it('handles menu data with only empty sections', () => {
      const emptyMenuData = {
        'Empty Section 1': { image: null, items: [] },
        'Empty Section 2': { image: null, items: [] }
      };

      const { getByText, queryByText } = render(<FeastMenuComponent menuData={emptyMenuData} />);
      
      // Menu title should be present
      expect(getByText('Menu')).toBeTruthy();
      
      // No section titles should be rendered
      expect(queryByText('Empty Section 1')).toBeNull();
      expect(queryByText('Empty Section 2')).toBeNull();
    });
  });

  // Key generation tests
  describe('Key Generation', () => {
    it('generates unique keys for sections', () => {
      const { getAllByText } = render(<FeastMenuComponent menuData={mockMenuData} />);
      
      const appetizersTitle = getAllByText('Appetizers');
      const mainCoursesTitle = getAllByText('Main Courses');
      
      expect(appetizersTitle.length).toBe(1);
      expect(mainCoursesTitle.length).toBe(1);
    });

    it('generates unique keys for menu items', () => {
      const { getAllByText } = render(<FeastMenuComponent menuData={mockMenuData} />);
      
      const saladItems = getAllByText('Salad');
      expect(saladItems.length).toBe(1);
    });
  });
});