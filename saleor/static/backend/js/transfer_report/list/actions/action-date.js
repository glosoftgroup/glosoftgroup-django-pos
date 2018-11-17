export const SET_DATE = 'SET_DATE';
export const SET_DATE_RANGE = 'SET_DATE_RANGE';

export const setDate = (payload) => ({
  type: SET_DATE,
  payload
});

export const setDateRange = (payload) => ({
  type: SET_DATE_RANGE,
  payload
});
