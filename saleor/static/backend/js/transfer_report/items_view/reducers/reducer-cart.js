import { ADD_ITEM, UPDATE_ITEM, DELETE_ITEM } from '../actions/action-cart';

const initialState = [];

export default (state = initialState, action) => {
  switch (action.type) {
    case ADD_ITEM:
      var add = true;
      state.map(item => {
        if (item.id === action.payload.id) {
          add = false;
          return;
        }
      });
      if (add) {
        return [...state, action.payload];
      } else {
        return state;
      }
    case UPDATE_ITEM:
      return state.map(item => {
        if (item.id === action.payload.id) return action.payload;
        return item;
      });
    case DELETE_ITEM:
      return state.filter(item => item.id !== action.itemId);
    default:
      return state;
  }
};
