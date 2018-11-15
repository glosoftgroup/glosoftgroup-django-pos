import api from '../api/Api';
/**
 * Constants
 */
export const SET_ITEMS = 'SET_ITEMS';
export const ADD_ITEM = 'ADD_ITEM';
export const UPDATE_ITEM = 'UPDATE_ITEM';

/**
 * Actions
 */
import { setChartOptions, setPie, setCounterChart } from '../actions';

export const setItems = (payload) => ({
  type: SET_ITEMS,
  payload
});

export const updateItem = (payload) => ({
  type: SET_ITEMS,
  payload
});

export const fetchItems = (params = {}) => {
  return dispatch => {
    // extract url parameters
    var url = '';
    if (typeof params === 'object') {
      if (Object.keys(params).length >= 1) {
        Object.keys(params).forEach(function(key) {
          url += key + '=' + params[key] + '&';
        });
        // remove last &
        url = url.slice(0, -1);
      }
    }
    /**
     * listing items
     */
    api.retrieve('/counter/transfer/report/api/list?' + url)
    .then(data => {
      data.loading = false;
      dispatch(setItems(data.data));
    })
    .catch(error => console.error(error));

    /**
     * fetch rechart graph data
     */
    api.retrieve(`/counter/transfer/report/api/graph/recharts/?${url}`)
    .then(response => { return response.data; })
    .then(data => {
      dispatch(setChartOptions(data));
    })
    .catch(error => console.error(error));

    /**
     * fetch Pie Chart data
     */
    api.retrieve(`/counter/transfer/report/api/graph/pie/?${url}`)
    .then(response => { return response.data; })
    .then(data => {
      dispatch(setPie(data));
    })
    .catch(error => console.error(error));

    /**
     * fetch counter graph data
     */
    api.retrieve(`/counter/transfer/report/api/graph/counter/?${url}`)
    .then(response => { return response.data; })
    .then(data => {
      dispatch(setCounterChart(data));
    })
    .catch(error => console.error(error));
  };
};
