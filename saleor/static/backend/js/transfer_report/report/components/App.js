import React from 'react';
import { Query } from 'react-apollo';
import gql from 'graphql-tag';

/**
 * COMPONENTS
 */
import Loader from './Loader';

/**
 * Containers
 */
import ItemList from '../containers/ItemList';

const ExchangeRates = () => (
  <Query
    query={gql`
    {
      allCounterTransfer(page: 1) {
        page
        pages
        total
        hasNext
        hasPrev
        results {
          id
          date
          counter {
            id
            name
          }
          counterTransferItems {
            id
            sku
            counter {
              id
              name
            }
          }
        }
      }
    }
    `}
  >
    {({ loading, error, data }) => {
      if (loading) return <Loader />;
      if (error) return <Loader />;
      console.log(data.allCounterTransfer.results);
      return <ItemList items={data.allCounterTransfer} />;
    }}
  </Query>
);

export default ExchangeRates;
