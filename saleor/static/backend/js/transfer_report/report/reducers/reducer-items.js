import { SET_ITEMS, ADD_ITEM, UPDATE_ITEM } from '../actions/action-items';

const initialState = {
  'links': {
    'next': null,
    'previous': null
  },
  'count': 7,
  'counter': '',
  'date': '',
  'loading': true,
  'total_pages': 1,
  'results': []
};

export default (state = initialState, action) => {
  switch (action.type) {
    case UPDATE_ITEM:
      return state.map(item => {
        if (item.id === action.payload.id) return action.payload;
        return item;
      });
    case ADD_ITEM:
      return { ...state };
    case SET_ITEMS:
      return action.payload;
    default:
      return state;
  }
};
