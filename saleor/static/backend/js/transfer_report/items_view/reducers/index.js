import { combineReducers } from 'redux';
import ItemReducer from './reducer-items';
import ItemSearch from './reducer-search';
import ItemDate from './reducer-date';
import ReducerCart from './reducer-cart';
import TransferDate from './reducer-transfer-date';

const allReducers = combineReducers({
  cart: ReducerCart,
  date: ItemDate,
  items: ItemReducer,
  search: ItemSearch,
  transferDate: TransferDate
});

export default allReducers;
