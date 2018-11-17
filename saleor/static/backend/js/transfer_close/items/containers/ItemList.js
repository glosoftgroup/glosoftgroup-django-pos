import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import Select2 from 'react-select2-wrapper';
import TransferTableRow from './TransferTableRow';
import TransferDate from './TransferDate';
import { addCartItem, deleteCartItem } from '../actions/action-cart';
import api from '../api/Api';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import ReactTooltip from 'react-tooltip';
import jGrowl from 'jgrowl';

class ItemList extends Component {
  /*
   * This component render panel group of accordions
   * Props: Listed in ItemList.propTypes below
   *        All props are fetch from redux
   * Usage: <ItemList />
   * */
  constructor(props) {
    super(props);
    this.state = {
      checked: '',
      allCleared: false,
      action: '1',
      actions: [
        {'text': 'Carry Forward', 'id': '1'},
        {'text': 'Return to Stock', 'id': '2'}
      ]
    };
  }
  componentDidMount() {
    try { jGrowl; } catch (error) {};
  }
  onSelectChange = (e) => {
    this.setState({
      [e.target.name]: e.target.value
    });
  }
  toggleCheckBox = () => {
    var checked = (this.state.checked === '') ? 'checked' : '';
    this.setState({checked});
    (checked === '') ? this.emptyToCart() : this.allToCart();
  }
  allToCart = () => {
    /* add all items to cart */
    var instance = { ...this.props };
    instance.items.results.map(obj => {
      this.props.addCartItem(obj);
    });
  }
  emptyToCart = () => {
    /* empty closing cart */
    var instance = { ...this.props };
    instance.items.results.map(obj => {
      this.props.deleteCartItem(obj.id);
    });
  }
  handleSubmit = (e) => {
    // bulk action here
    console.warn(this.props.date.date);
    var cart = this.props.cart;
    if (this.props.cart.length === 0) {
      var msg = 'Please check on trasferred item(s) that you want to close. Closing Cart is empty';
      $.jGrowl(msg, {
        header: 'Please Check transferred items',
        theme: 'bg-danger'
      });
      return;
    }
    if (this.state.action === '') {
      $.jGrowl('Please select closing action.', {
        header: 'Select action',
        theme: 'bg-danger'
      });
      return;
    }
    var pk = this.props.items.instance_id;
    // var items = { action: pk, cart: cart };
    var formData = new FormData();
    formData.append('action', this.state.action);
    formData.append('date', this.props.date.date);
    formData.append('items', JSON.stringify(cart));
    api.update('/counter/transfer/api/update/' + pk + '/', formData)
    .then(response => {
      window.location.reload();
    })
    .catch(error => {
      console.error(error);
    });
  }
  render() {
    return (
      <div className=" animated fadeIn panel-group panel-group-control panel-group-control-right content-group-lg">
        <div className="col-md-8 text-bold ">
        <ToastContainer />
          <div className="row">
            <div className="col-md-2 bulk-actions no-print ">
              <label>
              <div className="all no-print ">
                <div onClick={this.toggleCheckBox} className="">
                  <span className={this.state.checked}>
                    <input className="styled" type="checkbox" />
                  </span>
                </div>
              </div>
              </label>&nbsp;&nbsp;
              check all
            </div>
            <div className="col-md-3 no-print ">
                <Select2
                  data={ this.state.actions }
                  onChange={ this.onSelectChange }
                  value={ this.state.action }
                  name="action"
                  options={{
                    minimumResultsForSearch: -1,
                    placeholder: 'Select action'
                  }}
                />
            </div>
            <div className="col-md-3 no-print">
             <TransferDate itemsDate={this.props.items.date}/>
            </div>
            <div className="col-md-1 no-print" data-tip="Close selected items">
                <button onClick={this.handleSubmit} className="btn btn-primary bg-primary">Apply</button>
            </div>
          </div>
        </div>
        <div className="col-md-4">
        <h6 className="text-bold text-center">
         <span className="text-bold text-primary">DATE: </span>
         {this.props.items.date} &nbsp;
         <span className="text-bold text-primary">SHOP: </span>
         {this.props.items.counter}
        </h6>
        </div>
        <div className="col-md-4"></div>
        <h2 className="col-md-12 text-center text-bold yes-print">
        Transferred Item Closing Report
        </h2>
        <ReactTooltip place="bottom"/>
        <table className="table table-hover table-xs">
          <thead>
            <tr className="bg-primary">
              <th>.</th>
              <th>Product</th>
              <th>Cost Price</th>
              <th>Transferred Qty</th>
              <th>Sold</th>
              <th>Actual Qty</th>
              <th>Expected Qty</th>
              <th>Deficit/Surplus</th>
              <th>Note</th>
            </tr>
          </thead>
          <tbody>
          {this.props.items.results.map(obj => {
            return (
                  <TransferTableRow instance={obj}/>
            );
          })
          }
          <tr>
            <td colSpan={10}>
            {this.props.items.results.length === 0 &&
            <div className="text-center">
              {this.props.items.loading &&
                <h4 className="text-bold">Loading...</h4>
              }
              {!this.props.items.loading &&
                <h4 className="text-bold">No data Found</h4>
              }
            </div>
            }
            </td>
          </tr>
          </tbody>
        </table>
      </div>
    );
  }
}

ItemList.propTypes = {
  addCartItem: PropTypes.func.isRequired,
  cart: PropTypes.array.isRequired,
  items: PropTypes.array.isRequired,
  deleteCartItem: PropTypes.func.isRequired,
  date: PropTypes.array.isRequired
};
function mapStateToProps(state) {
  return {
    items: state.items,
    cart: state.cart,
    date: state.transferDate
  };
}

function matchDispatchToProps(dispatch) {
  return bindActionCreators({addCartItem, deleteCartItem}, dispatch);
}
export default connect(mapStateToProps, matchDispatchToProps)(ItemList);
