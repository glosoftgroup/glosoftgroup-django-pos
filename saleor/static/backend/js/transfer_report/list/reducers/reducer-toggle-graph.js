import { TOGGLE_MODE } from '../actions';

const initialState = { open: true };

export default function (state = initialState, action) {
  switch (action.type) {
    case TOGGLE_MODE:
      return action.payload;
  }
  return state;
};
