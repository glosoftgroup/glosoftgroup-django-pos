import { SET_ITEMS, ADD_ITEM } from '../actions/action-items';

const initialState = {
  'links': {
    'next': null,
    'previous': null
  },
  'count': 7,
  'total_pages': 1,
  'loading': true,
  'results': []
};

export default (state = initialState, action) => {
  switch (action.type) {
    case ADD_ITEM:
      return { ...state };
    case SET_ITEMS:
      return action.payload;
    default:
      return state;
  }
};
