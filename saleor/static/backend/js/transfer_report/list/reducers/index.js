import { combineReducers } from 'redux';
import ItemReducer from './reducer-items';
import ItemSearch from './reducer-search';
import ItemDate from './reducer-date';
import charts from './reducer-charts';
import pie from './reducer-pie';
import mode from './reducer-mode';
import openGraph from './reducer-toggle-graph';
import counterGraph from './reducer-counter-chart';
import counter from './reducer-counter';

const allReducers = combineReducers({
  items: ItemReducer,
  search: ItemSearch,
  date: ItemDate,
  charts: charts,
  mode,
  pie,
  openGraph,
  counterGraph,
  counter
});

export default allReducers;
