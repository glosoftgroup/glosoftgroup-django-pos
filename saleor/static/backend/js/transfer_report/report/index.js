import React from 'react';
import ReactDom from 'react-dom';
import { Provider } from 'react-redux';
import { ApolloProvider } from 'react-apollo';
/**
 * COMPONENTS
 */
import App from './components/App';

/**
 * STORE
 */
import store from './store';

/**
 * UTILs
 */
import client from './utils/apollo';

ReactDom.render(
  <ApolloProvider client={client}>
    <Provider store={store} >
        <App />
    </Provider>
  </ApolloProvider>,
  document.getElementById('root')
);
