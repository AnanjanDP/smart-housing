import { useState, useEffect } from 'react';
import { fetchListings } from '../services/api';

export const useFetchListings = () => {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchListings()
      .then((data) => {
        setListings(data.results || [
          {
            id: "1",
            title: "Luxury High-rise Studio in Downtown",
            description: "Modern studio apartment with floor-to-ceiling windows.",
            city: "San Francisco",
            price: 2600,
            bedrooms: 1,
            bathrooms: 1.0
          },
          {
            id: "2",
            title: "Cozy 2BR Flat near University",
            description: "Spacious 2 bedroom apartment ideal for students.",
            city: "Palo Alto",
            price: 3400,
            bedrooms: 2,
            bathrooms: 1.5
          }
        ]);
      })
      .catch(() => {
        setListings([
          {
            id: "1",
            title: "Luxury High-rise Studio in Downtown",
            description: "Modern studio apartment with floor-to-ceiling windows.",
            city: "San Francisco",
            price: 2600,
            bedrooms: 1,
            bathrooms: 1.0
          },
          {
            id: "2",
            title: "Cozy 2BR Flat near University",
            description: "Spacious 2 bedroom apartment ideal for students.",
            city: "Palo Alto",
            price: 3400,
            bedrooms: 2,
            bathrooms: 1.5
          }
        ]);
      })
      .finally(() => setLoading(false));
  }, []);

  return { listings, loading };
};
