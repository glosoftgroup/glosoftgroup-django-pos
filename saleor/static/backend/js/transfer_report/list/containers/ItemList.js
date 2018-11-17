import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import TransferTableRow from './TransferTableRow';
import ReactTooltip from 'react-tooltip';

class ItemList extends Component {
  /*
   * This component render panel group of accordions
   * Props: Listed in ItemList.propTypes below
   *        All props are fetch from redux
   *  Usage: <ItemList />
   * */
  render() {
    return (
      <div className={'panel-group panel-group-control panel-group-control-right content-group-lg ' + this.props.openGraph.open}>
      <ReactTooltip place="bottom"/>
        <table className="table table-hover table-xs">
          <thead>
            <tr className="bg-primary">
              <th data-tip="Transfer date">Date</th>
              <th data-tip="SHop name">Shop</th>
              <th data-tip="Total transferred quantity">Transferred qty</th>
              <th data-tip="Total sold quantity">Sold qty</th>
              <th data-tip="Total sale">Total Sale</th>
              <th data-tip="Transferred Items total cost price">Worth</th>
              <th>Status</th>
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
            <td colSpan={8}>
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
  items: PropTypes.array.isRequired,
  openGraph: PropTypes.object.isRequired
};
function mapStateToProps(state) {
  return {
    items: state.items,
    openGraph: state.openGraph
  };
}

function matchDispatchToProps(dispatch) {
  return bindActionCreators({}, dispatch);
}
export default connect(mapStateToProps, matchDispatchToProps)(ItemList);
