import React, { Component } from 'react';
import TransferCart from '../containers/TransferCart';
import ItemSearch from '../containers/ItemSearch';
import '../css/styles.scss';
class App extends Component {
  render() {
    return (
        <div className="row">
            <div className="col-md-7 transfer-products-wrapper">
              <ItemSearch />
            </div>
            <div className="col-md-5 transfer-cart-wrapper">
              <TransferCart />
            </div>
        </div>
    );
  }
}

export default App;
