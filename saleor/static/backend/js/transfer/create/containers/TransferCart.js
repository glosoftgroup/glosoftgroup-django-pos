import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { Quantity } from './Quantity';
import FilterDate from './FilterDate';
import { TransferButton } from './TransferButton';
import Select2 from 'react-select2-wrapper';
import { updateCartItem, deleteCartItem } from '../actions/action-cart';
import { getTotalQty, getTotalWorth } from '../reducers';
import { setCounter } from '../actions/action-counter';
import api from '../api/Api';

class TransferCart extends Component {
  constructor(props) {
    super(props);
    this.state = {
      totalQty: 0,
      totalWorth: 0,
      counter: '',
      closedCouters: '',
      openCounters: '',
      allCounters: [{fake: 'counter'}]
    };
  }
  componentWillMount() {
    this.getCounters();
  }
  getCounters = () => {
    api.retrieve('/counter/api/list')
    .then((response) => { return response.data.results; })
    .then((response) => {
      var allCounters = response;
      var closedCouters = [];
      var openCounters = [];
      response.map((value, index) => {
        delete value.description;
        delete value.delete_url;
        delete value.update_url;
        if (value.is_closed) {
          closedCouters.push(value);
        } else {
          openCounters.push(value);
        }
      });
      this.setState({closedCouters, openCounters, allCounters});
    })
    .catch((error) => { console.log(error); });
  }
  selectOptions = (url, placeholder) => {
    return {
      placeholder: placeholder,
      allowClear: true,
      width: '100%',
      dropdownAutoWidth: true,
      formatSelection: function(item) { return item.name; },
      formatResult: function(item) { return item.name; },
      ajax: {
        url: function (params) {
          return url + '?' + params.term;
        },
        processResults: function (data) {
          // self.refs.counter.el.empty();
          // Tranforms the top-level key of the response object from 'items' to 'results'
          data = data.results;
          return {
            results:
                data.map(function(item) {
                  return {
                    id: item.id,
                    text: item.name
                  };
                }
            )};
        }
      },
      debug: true,
      delay: 250
    };
  }
  deleteItem = id => {
    this.props.deleteCartItem(id);
  }
  handleSelectChange = (e) => {
    var value = e.target.value;
    this.setState({
      [e.target.name]: value
    });
    var payload = { id: value };
    this.props.setCounter(payload);
  }
  render() {
    return (
      <div className="product-cart-panel">
        {this.state.openCounters.length !== 0 &&
         <div className="alert alert-warning no-border text-center">
           <button type="button" className="close" data-dismiss="alert"><span>×</span><span className="sr-only">Close</span></button>
           <span className="text-semibold">Heads up!</span> Some shops's previous transfers were not closed. <a href="/counter/transfer/close/" className="alert-link"> Close them to enable transfer to those shops</a>.
         </div>
        }
        {this.state.allCounters.length === 0 &&
        <div className="alert alert-warning no-border text-center">
          <button type="button" className="close" data-dismiss="alert"><span>×</span><span className="sr-only">Close</span></button>
          <span className="text-semibold">Heads up!</span> Did you forget to add shops?<br/> <a href="/counter/" className="alert-link"> Click to add shop(s)</a>.
        </div>
        }
        {this.props.cart.length !== 0 &&
        <div >
          <div className="panel panel-body counter-panel">
            <div className="col-md-2 transfer-to-padding">
             <span className="text-bold">
               Date:
             </span>
            </div>
            <div className="col-md-4">
              <FilterDate/>
            </div>
           <div className="col-md-2 transfer-to-padding">
             <span className="text-bold">
               Shop:
             </span>
           </div>
           <div className="col-md-4">
           <Select2 ref="counter"
              onChange = {this.handleSelectChange}
              name = 'counter'
              value = {this.state.counter}
              options={{
                minimumResultsForSearch: -1,
                width: '100%',
                placeholder: 'Select Shop'
              }}
              data={ this.state.closedCouters}/>
           </div>
          </div>
          <div className="table-responsive">
              <table className="table table-xs table-hover">
                  <thead>
                      <tr className="bg-primary">
                          <th>Product</th>
                          <th>SKU</th>
                          <th>Quantity</th>
                          <th>Remove</th>
                      </tr>
                  </thead>
                  <tbody>
                  {this.props.cart.map(obj => {
                    return (
                      <tr key={obj.id}>
                          <td>{obj.productName}</td>
                          <td>{obj.sku}</td>
                          <td>
                            <Quantity
                            updateCartItem={(obj) => this.props.updateCartItem(obj) }
                            instance={obj}
                            cart={this.props.cart}
                            />
                          </td>
                          <td onClick={ () => this.deleteItem(obj.id)}>
                            <i className="animated shake icon-trash cursor-pointer"></i>
                          </td>
                      </tr>
                    );
                  })
                  }
                  </tbody>
              </table>

          </div>
          <div className="row transfer-section text-center mt-25">
            <div className="col-md-6">
                <div className="transfer-details">
                  <table className="table table-hover table-xm">
                    <thead>
                      <tr>
                        <th>Quantity</th>
                        <th>Worth</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>{this.props.totalQty}</td>
                        <td>{this.props.totalWth}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
            </div>
            <div className="col-md-6">
              <TransferButton closedCouters={this.state.closedCouters} date={this.props.date} cart={this.props.cart} counter={this.props.counter} />
            </div>
          </div>
        </div>
        }
        {this.props.cart.length === 0 &&
        <div className="order-empty text-center">
            <i className="animated shake icon-cart icon-3x"></i>
            <br />
            <h1 className="mt-15">
                Your transfer cart is empty
            </h1>
        </div>
        }
      </div>
    );
  }
}

TransferCart.propTypes = {
  cart: PropTypes.array.isRequired,
  counter: PropTypes.object,
  date: PropTypes.string.isRequired,
  totalQty: PropTypes.number.isRequired,
  totalWth: PropTypes.number.isRequired,
  updateCartItem: PropTypes.func.isRequired,
  setCounter: PropTypes.func.isRequired,
  deleteCartItem: PropTypes.func.isRequired
};
function mapStateToProps(state) {
  return {
    cart: state.cart,
    counter: state.counter,
    date: state.date,
    totalQty: getTotalQty(state),
    totalWth: getTotalWorth(state)
  };
}

function matchActionsToProps(dispatch) {
  return bindActionCreators({
    setCounter,
    updateCartItem,
    deleteCartItem
  }, dispatch);
}

export default connect(mapStateToProps, matchActionsToProps)(TransferCart);
